"""Domain errors. Messages are static so they can never carry applicant PII."""


class InvalidApplicationError(ValueError):
    """An adoption application would violate a domain invariant."""
