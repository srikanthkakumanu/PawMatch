"""HTTP request and response models."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, StrictBool, StrictStr

from pawmatch.domain.application import AdoptionApplication, Animal
from pawmatch.domain.decision import ScreeningDecision


class AnimalRequest(BaseModel):
    species: StrictStr
    weight_lbs: Decimal | None = Field(default=None, max_digits=12)


class ApplicationRequest(BaseModel):
    applicant_name: StrictStr
    address: StrictStr
    income: Decimal | None = Field(default=None, max_digits=14)
    # Strict, so a string such as "no" cannot be coerced into a screening input.
    has_fenced_yard: StrictBool
    has_prior_return: StrictBool
    animals: list[AnimalRequest]

    def to_domain(self) -> AdoptionApplication:
        return AdoptionApplication(
            applicant_name=self.applicant_name,
            address=self.address,
            income=self.income,
            has_fenced_yard=self.has_fenced_yard,
            has_prior_return=self.has_prior_return,
            animals=tuple(
                Animal(species=animal.species, weight_lbs=animal.weight_lbs)
                for animal in self.animals
            ),
        )


class DecisionResponse(BaseModel):
    application_id: UUID
    decision: ScreeningDecision
