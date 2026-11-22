"""API behavior, including the rule that PII never appears in responses."""

from typing import Any
from uuid import uuid4

from fastapi.testclient import TestClient

from pawmatch.application.errors import RepositoryError
from pawmatch.application.use_cases import GetDecision, SubmitApplication
from pawmatch.interface.api import create_app
from tests.conftest import FakeApplicationRepository

NAME = "Sentinel Applicant"
ADDRESS = "99 Sentinel Road"


def payload(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "applicant_name": NAME,
        "address": ADDRESS,
        "income": "54321",
        "has_fenced_yard": True,
        "has_prior_return": False,
        "animals": [{"species": "dog", "weight_lbs": 20}],
    }
    return body | overrides


def assert_no_pii(text: str) -> None:
    for value in (NAME, ADDRESS, "54321"):
        assert value not in text


def test_submit_then_read_decision_returns_decision_only(client: TestClient) -> None:
    created = client.post("/applications", json=payload(has_prior_return=True))
    assert created.status_code == 201
    assert_no_pii(created.text)

    application_id = created.json()["application_id"]
    read = client.get(f"/applications/{application_id}/decision")
    assert read.status_code == 200
    assert read.json() == {"application_id": application_id, "decision": "home_visit_required"}
    assert_no_pii(read.text)


def test_clear_application_goes_to_standard_review(client: TestClient) -> None:
    response = client.post("/applications", json=payload())
    assert response.json()["decision"] == "standard_review"


def test_unknown_application_is_404(client: TestClient) -> None:
    assert client.get(f"/applications/{uuid4()}/decision").status_code == 404


def test_malformed_id_is_422(client: TestClient) -> None:
    assert client.get("/applications/not-a-uuid/decision").status_code == 422


def test_request_validation_error_does_not_echo_input(client: TestClient) -> None:
    response = client.post("/applications", json=payload(has_fenced_yard=NAME, income=ADDRESS))
    assert response.status_code == 422
    assert_no_pii(response.text)


def test_domain_validation_error_does_not_echo_input(client: TestClient) -> None:
    response = client.post("/applications", json=payload(animals=[]))
    assert response.status_code == 422
    assert_no_pii(response.text)


def test_species_outside_fixed_list_is_rejected_and_not_stored(
    client: TestClient, repository: FakeApplicationRepository
) -> None:
    animals = [{"species": "puppy", "weight_lbs": 45}]
    response = client.post("/applications", json=payload(has_fenced_yard=False, animals=animals))
    assert response.status_code == 422
    assert "puppy" not in response.text
    assert repository.applications == {}


def test_string_cannot_be_coerced_into_screening_boolean(client: TestClient) -> None:
    assert client.post("/applications", json=payload(has_fenced_yard="no")).status_code == 422


def test_store_failure_is_503_without_details() -> None:
    class FailingRepository(FakeApplicationRepository):
        def save(self, *_args: Any) -> None:
            raise RepositoryError("The application store is unavailable.")

    repository = FailingRepository()
    app = create_app(
        SubmitApplication(repository), GetDecision(repository), check_ready=lambda: None
    )
    with TestClient(app) as test_client:
        response = test_client.post("/applications", json=payload())
    assert response.status_code == 503
    assert_no_pii(response.text)
