"""Tests for requires_home_visit and the AdoptionApplication/Animal invariants."""

from decimal import Decimal

import pytest

from pawmatch.domain.application import Animal
from pawmatch.domain.errors import InvalidApplicationError
from pawmatch.domain.home_visit import requires_home_visit
from tests.conftest import make_application


def dog(weight: str) -> Animal:
    return Animal("dog", Decimal(weight))


# One flag per rule


def test_home_visit_flagged_for_heavy_dog_without_fenced_yard() -> None:
    application = make_application(has_fenced_yard=False, animals=(dog("60"),))
    assert requires_home_visit(application) is True


def test_home_visit_flagged_for_prior_return() -> None:
    application = make_application(has_prior_return=True)
    assert requires_home_visit(application) is True


def test_home_visit_flagged_for_more_than_two_animals() -> None:
    application = make_application(animals=(dog("10"), dog("10"), dog("10")))
    assert requires_home_visit(application) is True


# 40 lb boundary without a fenced yard


@pytest.mark.parametrize(
    ("weight", "expected"),
    [("39.99", False), ("40", False), ("40.01", True)],
)
def test_home_visit_dog_weight_boundary_without_fenced_yard(weight: str, expected: bool) -> None:
    application = make_application(has_fenced_yard=False, animals=(dog(weight),))
    assert requires_home_visit(application) is expected


def test_home_visit_not_flagged_for_heavy_dog_with_fenced_yard() -> None:
    application = make_application(has_fenced_yard=True, animals=(dog("90"),))
    assert requires_home_visit(application) is False


def test_home_visit_flagged_when_one_of_two_dogs_is_heavy_without_fenced_yard() -> None:
    # Decision of 2026-11-23: any one dog over 40 lb counts. Two animals, so count is not the cause.
    application = make_application(has_fenced_yard=False, animals=(dog("20"), dog("41")))
    assert requires_home_visit(application) is True


def test_home_visit_not_flagged_for_heavy_non_dog_without_fenced_yard() -> None:
    application = make_application(
        has_fenced_yard=False, animals=(Animal("other", Decimal("200")),)
    )
    assert requires_home_visit(application) is False


# Animal count


def test_home_visit_not_flagged_for_one_animal() -> None:
    application = make_application(animals=(dog("10"),))
    assert requires_home_visit(application) is False


def test_home_visit_not_flagged_for_two_animals() -> None:
    application = make_application(animals=(dog("10"), Animal("cat")))
    assert requires_home_visit(application) is False


def test_home_visit_flagged_for_three_mixed_animals() -> None:
    application = make_application(animals=(dog("10"), Animal("cat"), Animal("other")))
    assert requires_home_visit(application) is True


# Clear pass


def test_home_visit_clear_pass_is_not_flagged() -> None:
    assert requires_home_visit(make_application()) is False


# Invalid applications


def test_home_visit_invalid_blank_name_raises() -> None:
    with pytest.raises(InvalidApplicationError):
        make_application(applicant_name="   ")


def test_home_visit_invalid_no_animals_raises() -> None:
    with pytest.raises(InvalidApplicationError):
        make_application(animals=())


def test_home_visit_invalid_negative_dog_weight_raises() -> None:
    with pytest.raises(InvalidApplicationError):
        make_application(animals=(dog("-1"),))


def test_home_visit_invalid_dog_without_weight_raises() -> None:
    with pytest.raises(InvalidApplicationError):
        make_application(animals=(Animal("dog"),))


@pytest.mark.parametrize("species", ["puppy", "dgo", "German Shepherd", "dogs", "", "   "])
def test_home_visit_invalid_species_outside_fixed_list_raises(species: str) -> None:
    with pytest.raises(InvalidApplicationError):
        Animal(species, Decimal("45"))


@pytest.mark.parametrize("species", ["dog", "Dog", " DOG "])
def test_home_visit_species_is_normalized_so_rule_still_applies(species: str) -> None:
    application = make_application(has_fenced_yard=False, animals=(Animal(species, Decimal("45")),))
    assert requires_home_visit(application) is True
