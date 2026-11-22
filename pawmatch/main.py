"""Composition root: the only place an adapter is wired to a port."""

from pawmatch.application.use_cases import GetDecision, SubmitApplication
from pawmatch.infrastructure.config import load_settings
from pawmatch.infrastructure.postgres_repository import PostgresApplicationRepository
from pawmatch.interface.api import create_app

_settings = load_settings()
_repository = PostgresApplicationRepository(_settings.database_url)

app = create_app(
    submit_application=SubmitApplication(_repository),
    get_decision=GetDecision(_repository),
    check_ready=_repository.check_ready,
    prepare=_repository.ensure_schema,
)
