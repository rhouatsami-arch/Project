"""Central FastAPI exception handlers — predictable JSON error responses."""

from __future__ import annotations

import logging
import os
import traceback

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.exceptions import AppError

logger = logging.getLogger("matioushire.errors")
DEBUG = os.getenv("DEBUG", "false").lower() in {"1", "true", "yes"}


def _error_body(
    *,
    code: str,
    message: str,
    status_code: int,
    details: dict[str, object] | list[object] | None = None,
) -> dict[str, object]:
    body: dict[str, object] = {
        "error": {
            "code": code,
            "message": message,
            "status": status_code,
        }
    }
    if details:
        body["error"]["details"] = details
    return body


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(
                code=exc.code,
                message=exc.message,
                status_code=exc.status_code,
                details=exc.details or None,
            ),
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(
        _request: Request, exc: HTTPException
    ) -> JSONResponse:
        detail = exc.detail
        if isinstance(detail, dict):
            message = str(detail.get("message", detail))
            code = str(detail.get("code", "http_error"))
            details = detail
        elif isinstance(detail, list):
            message = "Request validation failed"
            code = "http_error"
            details = detail
        else:
            message = str(detail)
            code = "http_error"
            details = None

        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(
                code=code,
                message=message,
                status_code=exc.status_code,
                details=details,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = [
            {
                "field": ".".join(str(part) for part in err.get("loc", ())[1:]),
                "message": err.get("msg", "Invalid value"),
                "type": err.get("type", "value_error"),
            }
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_body(
                code="validation_error",
                message="Invalid request payload",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                details={"fields": errors},
            ),
        )

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(
        _request: Request, exc: IntegrityError
    ) -> JSONResponse:
        logger.warning("Database integrity error: %s", exc.orig)
        message = "Resource conflict or constraint violation"
        if "UNIQUE" in str(exc.orig).upper() or "unique" in str(exc).lower():
            message = "A record with this value already exists"
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=_error_body(
                code="conflict",
                message=message,
                status_code=status.HTTP_409_CONFLICT,
            ),
        )

    @app.exception_handler(SQLAlchemyError)
    async def handle_sqlalchemy_error(
        _request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        logger.exception("Database error: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=_error_body(
                code="database_error",
                message="Database operation failed. Please try again later.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            ),
        )

    @app.exception_handler(ValueError)
    async def handle_value_error(_request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=_error_body(
                code="invalid_value",
                message=str(exc),
                status_code=status.HTTP_400_BAD_REQUEST,
            ),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        _request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("Unhandled server error: %s", exc)
        details: dict[str, object] | None = None
        if DEBUG:
            details = {"traceback": traceback.format_exc()}
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_body(
                code="internal_error",
                message="An unexpected error occurred. Please try again later.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details=details,
            ),
        )
