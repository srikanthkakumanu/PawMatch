"""Application use cases."""

from dataclasses import dataclass
from uuid import UUID

from pawmatch.application.errors import ApplicationNotFoundError
from pawmatch.application.ports import ApplicationRepository
from pawmatch.domain.application import AdoptionApplication
from pawmatch.domain.decision import ScreeningDecision
from pawmatch.domain.home_visit import requires_home_visit


@dataclass(frozen=True, slots=True)
class DecisionResult:
    application_id: UUID
    decision: ScreeningDecision


class SubmitApplication:
    def __init__(self, repository: ApplicationRepository) -> None:
        self._repository = repository

    def execute(self, application: AdoptionApplication) -> DecisionResult:
        decision = (
            ScreeningDecision.HOME_VISIT_REQUIRED
            if requires_home_visit(application)
            else ScreeningDecision.STANDARD_REVIEW
        )
        self._repository.save(application, decision)
        return DecisionResult(application.id, decision)


class GetDecision:
    def __init__(self, repository: ApplicationRepository) -> None:
        self._repository = repository

    def execute(self, application_id: UUID) -> DecisionResult:
        decision = self._repository.get_decision(application_id)
        if decision is None:
            raise ApplicationNotFoundError("Application not found.")
        return DecisionResult(application_id, decision)
