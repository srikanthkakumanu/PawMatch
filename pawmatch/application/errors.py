"""Use-case and port errors. Messages are static and carry no applicant data."""


class ApplicationNotFoundError(LookupError):
    """No application exists with the requested ID."""


class RepositoryError(RuntimeError):
    """The application store could not complete an operation."""
