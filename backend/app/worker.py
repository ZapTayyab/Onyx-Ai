"""Temporal Worker — runs evaluation workflows from the task queue."""

from __future__ import annotations

import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker, UnsandboxedWorkflowRunner

from app.config import get_config
from app.workflows.evaluation_workflow import EvaluationWorkflow, TASK_QUEUE

logger = logging.getLogger("snt_ai.worker")


async def run_worker_forever(temporal_client: Client) -> None:
    """Register EvaluationWorkflow and poll the task queue indefinitely."""
    worker = Worker(
        client=temporal_client,
        task_queue=TASK_QUEUE,
        workflows=[EvaluationWorkflow],
        workflow_runner=UnsandboxedWorkflowRunner(),
    )
    logger.info("Temporal worker starting on queue=%s", TASK_QUEUE)
    await worker.run()


async def main() -> None:
    config = get_config()
    logging.basicConfig(level=config.log_level.upper())

    logger.info(
        "Connecting to Temporal at %s (namespace=%s)",
        config.temporal_host,
        config.temporal_namespace,
    )
    client = await Client.connect(
        config.temporal_host,
        namespace=config.temporal_namespace,
    )
    logger.info("Connected")

    await run_worker_forever(client)


if __name__ == "__main__":
    asyncio.run(main())
