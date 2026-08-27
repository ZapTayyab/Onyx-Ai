from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import sqlalchemy
import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import ResponseValidationError

from app.config import RunStatus, get_config
from app.core.cache import cache_service
from app.core.clickhouse import clickhouse_mgr
from app.core.database import close_db, init_db, _get_session_factory
from app.core.exceptions import ErrorHandlingMiddleware
from app.core.logging import configure_logging
from app.core.temporal import init_temporal_client, close_temporal_client, get_temporal_client
from app.middleware.auth_middleware import OrganizationContextMiddleware
from app.middleware.rate_limiter import RateLimitMiddleware
from app.models.postgres import RunMetadata
from app.routers import agents, auth, evaluations, suites, organizations, billing

logger = logging.getLogger("snt_ai.main")

config = get_config()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    configure_logging()
    logger.info(
        "Starting SNT AI Assurance Platform [env=%s]",
        config.environment.value,
    )

    await init_db()
    await cache_service.initialize()
    await init_temporal_client()

    try:
        await clickhouse_mgr.connect()
        from app.models.clickhouse.traces import CREATE_TURN_TRACES_TABLE
        await clickhouse_mgr.execute(CREATE_TURN_TRACES_TABLE)
        logger.info("ClickHouse schema initialized")
    except Exception as exc:
        logger.warning("ClickHouse initialization failed (non-fatal): %s", exc)

    # Retry any evaluations that crashed in PENDING/RUNNING state on last shutdown
    try:
        factory = _get_session_factory()
        async with factory() as db:
            result = await db.execute(
                sqlalchemy.select(RunMetadata).where(
                    RunMetadata.status.in_([RunStatus.PENDING, RunStatus.RUNNING])
                )
            )
            stuck = result.scalars().all()
            for run in stuck:
                logger.warning(
                    "Resetting stuck evaluation run=%s (status=%s)", run.id, run.status.value
                )
                run.status = RunStatus.FAILED
                run.error_message = "Container restarted while evaluation was in progress"
            await db.commit()
            if stuck:
                logger.info("Reset %d stuck evaluation run(s)", len(stuck))
    except Exception as exc:
        logger.warning("Failed to check for stuck evaluation runs: %s", exc)

    yield

    await close_temporal_client()
    await close_db()
    await cache_service.close()
    clickhouse_mgr.close()
    logger.info("SNT AI Assurance Platform shutdown complete")


app = FastAPI(
    title=config.app_name,
    version="1.0.0",
    description="Enterprise AI Assurance & Evaluation Platform - "
    "Multi-tenant, distributed evaluation infrastructure for "
    "LLM safety, robustness, and regression testing.",
    lifespan=lifespan,
    docs_url="/docs" if config.is_development else None,
    redoc_url="/redoc" if config.is_development else None,
    contact={
        "name": config.company_name,
        "email": config.support_email,
    },
    license_info={
        "name": "Proprietary",
    },
)

@app.exception_handler(ResponseValidationError)
async def response_validation_handler(request: Request, exc: ResponseValidationError) -> JSONResponse:
    logger.exception("Response validation error for %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal error occurred. Please try again later."},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if config.is_development else config.cors_origins,
)

app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    max_requests=200,
    window_seconds=60,
    exclude_paths={"/health", "/metrics", "/docs", "/redoc", "/openapi.json"},
)
app.add_middleware(OrganizationContextMiddleware)

app.include_router(auth.router, prefix="/v1")
app.include_router(agents.router, prefix="/v1")
app.include_router(suites.router, prefix="/v1")
app.include_router(evaluations.router, prefix="/v1")
app.include_router(organizations.router, prefix="/v1")
app.include_router(billing.router, prefix="/v1")


@app.get("/health", tags=["System"])
async def health_check() -> dict:
    ch_healthy = await clickhouse_mgr.health_check()
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": config.environment.value,
        "database": "connected",
        "clickhouse": "connected" if ch_healthy else "unavailable",
        "auth_provider": config.auth_provider,
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.is_development,
        log_level=config.log_level.lower(),
    )
