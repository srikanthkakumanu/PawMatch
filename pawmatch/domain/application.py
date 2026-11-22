"""The AdoptionApplication entity."""

from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from pawmatch.domain.errors import InvalidApplicationError


class Species(StrEnum):
    """Fixed list (NOTES.md, 2026-11-23), so a dog cannot miss policy line 6 through free text."""

    # policies/screening-policy.md:6 "a dog over 40 lbs". Puppies and all breeds are entered as dog.
    DOG = "dog"
    CAT = "cat"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class Animal:
    species: Species | str
    weight_lbs: Decimal | None = None

    def __post_init__(self) -> None:
        try:
            species = Species(self.species.strip().casefold())
        except ValueError:
            raise InvalidApplicationError("Animal species must be dog, cat or other.") from None
        object.__setattr__(self, "species", species)

        if self.weight_lbs is not None and not self.weight_lbs.is_finite():
            raise InvalidApplicationError("Animal weight must be a finite number.")
        if self.is_dog and self.weight_lbs is None:
            # The fenced-yard rule cannot be evaluated without each dog's weight.
            raise InvalidApplicationError("Dog weight is required.")
        if self.weight_lbs is not None and self.weight_lbs < 0:
            raise InvalidApplicationError("Animal weight must not be negative.")

    @property
    def is_dog(self) -> bool:
        return self.species is Species.DOG


@dataclass(frozen=True, slots=True)
class AdoptionApplication:
    # repr=False keeps PII out of logs and tracebacks that format this entity.
    applicant_name: str = field(repr=False)
    address: str = field(repr=False)
    has_fenced_yard: bool
    has_prior_return: bool
    animals: tuple[Animal, ...]
    income: Decimal | None = field(default=None, repr=False)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.applicant_name.strip():
            raise InvalidApplicationError("Applicant name must not be blank.")
        if len(self.animals) < 1:
            raise InvalidApplicationError("An application needs at least one animal.")
