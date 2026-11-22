"""FastAPI routes and the mapping of errors to HTTP."""

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from pawmatch.application.errors import ApplicationNotFoundError, RepositoryError
from pawmatch.application.use_cases import DecisionResult, GetDecision, SubmitApplication
from pawmatch.domain.errors import InvalidApplicationError
from pawmatch.interface.schemas import ApplicationRequest, DecisionResponse


def _to_response(result: DecisionResult) -> DecisionResponse:
    return DecisionResponse(application_id=result.application_id, decision=result.decision)


def _register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def handle_request_validation(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # FastAPI's default body echoes the submitted input, which can contain PII.
        errors = [
            {
                "field": ".".join(str(part) for part in error["loc"][1:]),
                "problem": error["type"],
            }
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": "Invalid request.", "errors": errors},
        )

    @app.exception_handler(InvalidApplicationError)
    async def handle_invalid_application(
        _request: Request, exc: InvalidApplicationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content={"detail": str(exc)}
        )

    @app.exception_handler(ApplicationNotFoundError)
    async def handle_not_found(_request: Request, _exc: ApplicationNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": "Application not found."}
        )

    @app.exception_handler(RepositoryError)
    async def handle_repository_error(_request: Request, _exc: RepositoryError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Service temporarily unavailable."},
        )


def create_app(
    submit_application: SubmitApplication,
    get_decision: GetDecision,
    check_ready: Callable[[], None],
    prepare: Callable[[], None] | None = None,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        if prepare is not None:
            prepare()
        yield

    app = FastAPI(title="PawMatch", lifespan=lifespan)
    _register_error_handlers(app)

    @app.get("/health")
    def health() -> dict[str, str]:
        check_ready()
        return {"status": "ok"}

    @app.post("/applications", status_code=status.HTTP_201_CREATED)
    def submit(request: ApplicationRequest) -> DecisionResponse:
        return _to_response(submit_application.execute(request.to_domain()))

    @app.get("/applications/{application_id}/decision")
    def read_decision(application_id: UUID) -> DecisionResponse:
        return _to_response(get_decision.execute(application_id))

    return app
