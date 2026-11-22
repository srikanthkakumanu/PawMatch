"""Ports implemented by infrastructure adapters."""

from typing import Protocol
from uuid import UUID

from pawmatch.domain.application import AdoptionApplication
from pawmatch.domain.decision import ScreeningDecision


class ApplicationRepository(Protocol):
    def save(self, application: AdoptionApplication, decision: ScreeningDecision) -> None:
        """Store an application with its decision."""
        ...

    def get_decision(self, application_id: UUID) -> ScreeningDecision | None:
        """Return the stored decision, or None if the application does not exist."""
        ...
