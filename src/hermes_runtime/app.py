"""Local FastAPI runtime wrapper for deterministic finance workflows."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import BaseModel, ConfigDict
from starlette.exceptions import HTTPException as StarletteHTTPException

from hermes_finance import generate_daily_market_brief, generate_entry_zone_strategy


class ErrorDetail(BaseModel):
    """Normalized runtime error payload."""

    type: str
    message: str
    field: str | None = None


class ErrorEnvelope(BaseModel):
    """Top-level error response envelope."""

    error: ErrorDetail


class FinanceRequest(BaseModel):
    """Strict request shape for finance runtime endpoints."""

    model_config = ConfigDict(extra="forbid", strict=True)

    watchlist: list[str]
    as_of: str
    fixture: dict[str, Any]


class FinanceResponse(BaseModel):
    """Structured success payload for finance runtime endpoints."""

    workflow: str
    as_of: str
    report_markdown: str


class StatusResponse(BaseModel):
    """Structured health and readiness payload."""

    status: str


class DomainValidationError(Exception):
    """Expected finance-domain validation failure."""

    def __init__(self, message: str, field: str | None = None) -> None:
        self.message = message
        self.field = field
        super().__init__(message)


def _error_response(
    status_code: int,
    error_type: str,
    message: str,
    *,
    field: str | None = None,
) -> JSONResponse:
    payload = {"error": {"type": error_type, "message": message}}
    if field is not None:
        payload["error"]["field"] = field
    return JSONResponse(status_code=status_code, content=payload)


def _extract_field(validation_error: RequestValidationError) -> str | None:
    errors = validation_error.errors()
    if not errors:
        return None

    location = errors[0].get("loc", ())
    if len(location) >= 2 and location[0] == "body" and isinstance(location[1], str):
        return location[1]

    return None


def _validation_message(validation_error: RequestValidationError) -> str:
    errors = validation_error.errors()
    if not errors:
        return "Invalid request body."
    return errors[0].get("msg", "Invalid request body.")


def _has_required_finance_routes(app_instance: FastAPI) -> bool:
    required_routes = {
        ("/finance/daily-market-brief", "POST"),
        ("/finance/entry-zone-strategy", "POST"),
    }

    registered_routes = {
        (route.path, method)
        for route in app_instance.routes
        if isinstance(route, APIRoute)
        for method in route.methods
    }
    return required_routes.issubset(registered_routes)


def _validate_watchlist(watchlist: list[str]) -> None:
    if not watchlist:
        raise DomainValidationError("Watchlist is empty.", field="watchlist")


def _build_finance_response(
    workflow: str, as_of: str, report_markdown: str
) -> FinanceResponse:
    return FinanceResponse(
        workflow=workflow,
        as_of=as_of,
        report_markdown=report_markdown,
    )


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


@app.exception_handler(RequestValidationError)
async def handle_request_validation(
    request: Request, validation_error: RequestValidationError
) -> JSONResponse:
    del request
    return _error_response(
        422,
        "request_validation",
        _validation_message(validation_error),
        field=_extract_field(validation_error),
    )


@app.exception_handler(DomainValidationError)
async def handle_domain_validation(
    request: Request, domain_error: DomainValidationError
) -> JSONResponse:
    del request
    return _error_response(
        400,
        "domain_validation",
        domain_error.message,
        field=domain_error.field,
    )


@app.exception_handler(StarletteHTTPException)
async def handle_http_error(
    request: Request, http_error: StarletteHTTPException
) -> JSONResponse:
    del request
    if http_error.status_code == 404:
        return _error_response(404, "not_found", "Route not found.")
    if http_error.status_code == 405:
        return _error_response(405, "method_not_allowed", "Method not allowed.")
    return _error_response(
        http_error.status_code,
        "internal_error",
        "Internal runtime error.",
    )


@app.exception_handler(Exception)
async def handle_unexpected_error(
    request: Request, unexpected_error: Exception
) -> JSONResponse:
    del request
    del unexpected_error
    return _error_response(500, "internal_error", "Internal runtime error.")


@app.get("/health", response_model=StatusResponse)
async def health() -> StatusResponse:
    return StatusResponse(status="ok")


@app.get("/ready", response_model=StatusResponse)
async def ready() -> JSONResponse | StatusResponse:
    if _has_required_finance_routes(app):
        return StatusResponse(status="ready")
    return JSONResponse(status_code=503, content={"status": "not_ready"})


@app.post("/finance/daily-market-brief", response_model=FinanceResponse)
async def daily_market_brief(payload: FinanceRequest) -> FinanceResponse:
    _validate_watchlist(payload.watchlist)
    try:
        report_markdown = generate_daily_market_brief(
            payload.watchlist,
            payload.as_of,
            payload.fixture,
        )
    except ValueError as exc:
        raise DomainValidationError(str(exc)) from exc
    return _build_finance_response(
        "daily_market_brief", payload.as_of, report_markdown
    )


@app.post("/finance/entry-zone-strategy", response_model=FinanceResponse)
async def entry_zone_strategy(payload: FinanceRequest) -> FinanceResponse:
    _validate_watchlist(payload.watchlist)
    try:
        report_markdown = generate_entry_zone_strategy(
            payload.watchlist,
            payload.as_of,
            payload.fixture,
        )
    except ValueError as exc:
        raise DomainValidationError(str(exc)) from exc
    return _build_finance_response(
        "entry_zone_strategy", payload.as_of, report_markdown
    )
