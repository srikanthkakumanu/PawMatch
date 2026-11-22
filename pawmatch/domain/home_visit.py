"""Home-visit screening rule, from policies/screening-policy.md."""

from decimal import Decimal

from pawmatch.domain.application import AdoptionApplication

# policies/screening-policy.md:6 "a dog over 40 lbs". Exactly 40 lb does not match.
DOG_WEIGHT_LIMIT_LBS = Decimal(40)
# policies/screening-policy.md:8 "more than two animals". Exactly two does not match.
MAX_ANIMALS_WITHOUT_VISIT = 2


def requires_home_visit(application: AdoptionApplication) -> bool:
    """Return True when any documented screening criterion matches."""
    # policies/screening-policy.md:6. Any one dog counts (NOTES.md, 2026-11-23).
    if not application.has_fenced_yard and any(
        animal.is_dog and animal.weight_lbs > DOG_WEIGHT_LIMIT_LBS for animal in application.animals
    ):
        return True

    # policies/screening-policy.md:7. Any prior return counts, however old (NOTES.md, 2026-11-23).
    if application.has_prior_return:
        return True

    # policies/screening-policy.md:8.
    if len(application.animals) > MAX_ANIMALS_WITHOUT_VISIT:
        return True

    return False
