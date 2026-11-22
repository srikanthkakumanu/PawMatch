"""Postgres adapter for ApplicationRepository. The only SQL in the project."""

from collections.abc import Iterator
from contextlib import contextmanager
from uuid import UUID

import psycopg

from pawmatch.application.errors import RepositoryError
from pawmatch.domain.application import AdoptionApplication
from pawmatch.domain.decision import ScreeningDecision

_SCHEMA = """
CREATE TABLE IF NOT EXISTS adoption_applications (
    id uuid PRIMARY KEY,
    applicant_name text NOT NULL,
    address text NOT NULL,
    income numeric,
    has_fenced_yard boolean NOT NULL,
    has_prior_return boolean NOT NULL,
    decision text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS application_animals (
    application_id uuid NOT NULL REFERENCES adoption_applications (id) ON DELETE CASCADE,
    position smallint NOT NULL,
    species text NOT NULL,
    weight_lbs numeric,
    PRIMARY KEY (application_id, position)
);
"""


class PostgresApplicationRepository:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url

    @contextmanager
    def _connection(self) -> Iterator[psycopg.Connection]:
        try:
            with psycopg.connect(self._database_url, connect_timeout=5) as connection:
                yield connection
        except psycopg.Error:
            # Driver errors can quote row values or connection details, so drop them.
            raise RepositoryError("The application store is unavailable.") from None

    def ensure_schema(self) -> None:
        with self._connection() as connection:
            connection.execute(_SCHEMA)

    def check_ready(self) -> None:
        with self._connection() as connection:
            connection.execute("SELECT 1")

    def save(self, application: AdoptionApplication, decision: ScreeningDecision) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO adoption_applications
                    (id, applicant_name, address, income,
                     has_fenced_yard, has_prior_return, decision)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    application.id,
                    application.applicant_name,
                    application.address,
                    application.income,
                    application.has_fenced_yard,
                    application.has_prior_return,
                    decision.value,
                ),
            )
            with connection.cursor() as cursor:
                cursor.executemany(
                    """
                    INSERT INTO application_animals
                        (application_id, position, species, weight_lbs)
                    VALUES (%s, %s, %s, %s)
                    """,
                    [
                        (application.id, position, str(animal.species), animal.weight_lbs)
                        for position, animal in enumerate(application.animals)
                    ],
                )

    def get_decision(self, application_id: UUID) -> ScreeningDecision | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT decision FROM adoption_applications WHERE id = %s",
                (application_id,),
            ).fetchone()
        return ScreeningDecision(row[0]) if row else None
