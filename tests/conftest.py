"""Shared fixtures. The ApplicationRepository port is faked, so no Postgres is needed."""

from collections.abc import Iterator
from decimal import Decimal
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from pawmatch.application.use_cases import GetDecision, SubmitApplication
from pawmatch.domain.application import AdoptionApplication, Animal
from pawmatch.domain.decision import ScreeningDecision
from pawmatch.interface.api import create_app


class FakeApplicationRepository:
    def __init__(self) -> None:
        self.applications: dict[UUID, AdoptionApplication] = {}
        self.decisions: dict[UUID, ScreeningDecision] = {}

    def save(self, application: AdoptionApplication, decision: ScreeningDecision) -> None:
        self.applications[application.id] = application
        self.decisions[application.id] = decision

    def get_decision(self, application_id: UUID) -> ScreeningDecision | None:
        return self.decisions.get(application_id)


def make_application(
    applicant_name: str = "Test Applicant",
    address: str = "1 Test Street",
    income: Decimal | None = Decimal("50000"),
    has_fenced_yard: bool = True,
    has_prior_return: bool = False,
    animals: tuple[Animal, ...] | None = None,
) -> AdoptionApplication:
    """Build a valid application that matches no screening criterion by default."""
    return AdoptionApplication(
        applicant_name=applicant_name,
        address=address,
        income=income,
        has_fenced_yard=has_fenced_yard,
        has_prior_return=has_prior_return,
        animals=(Animal("dog", Decimal("20")),) if animals is None else animals,
    )


@pytest.fixture
def repository() -> FakeApplicationRepository:
    return FakeApplicationRepository()


@pytest.fixture
def client(repository: FakeApplicationRepository) -> Iterator[TestClient]:
    app = create_app(
        submit_application=SubmitApplication(repository),
        get_decision=GetDecision(repository),
        check_ready=lambda: None,
    )
    with TestClient(app) as test_client:
        yield test_client
