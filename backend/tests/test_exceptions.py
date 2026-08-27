from __future__ import annotations

from fastapi import HTTPException, status

from app.core.exceptions import (
    ConflictError,
    ErrorHandlingMiddleware,
    ForbiddenError,
    NotFoundError,
    ServiceUnavailableError,
    ValidationError,
)


class TestExceptions:
    def test_not_found_error(self) -> None:
        exc = NotFoundError("Custom not found")
        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert exc.detail == "Custom not found"

    def test_not_found_default_message(self) -> None:
        exc = NotFoundError()
        assert exc.detail == "Resource not found"

    def test_conflict_error(self) -> None:
        exc = ConflictError("Already exists")
        assert exc.status_code == status.HTTP_409_CONFLICT
        assert exc.detail == "Already exists"

    def test_conflict_default_message(self) -> None:
        exc = ConflictError()
        assert exc.detail == "Resource already exists"

    def test_validation_error(self) -> None:
        exc = ValidationError("Invalid input")
        assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert exc.detail == "Invalid input"

    def test_forbidden_error(self) -> None:
        exc = ForbiddenError("Access denied")
        assert exc.status_code == status.HTTP_403_FORBIDDEN
        assert exc.detail == "Access denied"

    def test_service_unavailable_error(self) -> None:
        exc = ServiceUnavailableError("Down for maintenance")
        assert exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert exc.detail == "Down for maintenance"

    def test_exceptions_are_http_exceptions(self) -> None:
        assert isinstance(NotFoundError(), HTTPException)
        assert isinstance(ConflictError(), HTTPException)
        assert isinstance(ValidationError(), HTTPException)
        assert isinstance(ForbiddenError(), HTTPException)
        assert isinstance(ServiceUnavailableError(), HTTPException)

    def test_error_handling_middleware_instantiation(self) -> None:
        middleware = ErrorHandlingMiddleware(app=None)
        assert middleware is not None
