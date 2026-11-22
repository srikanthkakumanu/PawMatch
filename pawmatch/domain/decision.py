"""The outcome of screening. It never approves or rejects an application."""

from enum import StrEnum


class ScreeningDecision(StrEnum):
    HOME_VISIT_REQUIRED = "home_visit_required"
    STANDARD_REVIEW = "standard_review"
