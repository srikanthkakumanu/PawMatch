
# PLAN.md — Auto-flag applications needing a home visit

Status: approved by the adoptions manager, 2026-08-07. Revised and re-approved 2026-11-23 by the adoptions manager or their delegate. The main session performs feature-author's steps, by the same approval.

## Objective

Applications that match the documented screening criteria are flagged for a
mandatory home visit. All others go to standard review. Screening never approves
or rejects an application: a person always makes that call.

## Constraints

- Criteria come from policies/screening-policy.md through rag_query, never from memory.
- The rule lives in pawmatch/domain/home_visit.py; SubmitApplication only calls it. No layer imports outward.
- No applicant PII in logs, error messages or GET responses (CLAUDE.md).

## Prerequisite: application scaffold (approved 2026-11-23)

The repo has no application code yet, and steps 2 to 5 and the quality gates depend on it.
Step 0 builds only what they need. It adds no screening logic. Owner: feature-author.

0a. Project: a uv project on Python 3.15 (`pyproject.toml`, `uv.lock`) with pytest and ruff as dev dependencies, and the `pawmatch/` packages. Tests run with `uv run pytest`.
0b. Domain: `AdoptionApplication` (validated in `__post_init__`) and `ScreeningDecision`.
0c. Application: the `ApplicationRepository` port, `SubmitApplication` and `GetDecision`.
0d. Infrastructure: `PostgresApplicationRepository` (the only SQL, with idempotent table creation) and environment config.
0e. Interface: `POST` an application and `GET` its decision, with pydantic request models, error mapping in `pawmatch/interface/api.py`, and `docs/api-reference.md`. `GET` returns the decision only.
0f. Composition: `pawmatch/main.py` is the only place the adapter is wired to the port.
0g. Tests: `tests/conftest.py` (fake repository, `make_application`) and `tests/test_architecture.py`.
0h. Containers: non-root `Dockerfile`, `docker-compose.yml` (services `api` and `db`, a named Postgres volume, `DB_PORT`, and a required `POSTGRES_PASSWORD`), and `render.yaml`. The `api` service receives only `DATABASE_URL` and `PORT`, and other `.env` entries are ignored. Nothing is deployed.

Application IDs are random UUIDs, so one applicant's ID cannot be guessed from another's.

Policy decisions for 0b (2026-11-23, see NOTES.md):

- Each dog's weight is stored. Without a fenced yard, any one dog over 40 lb triggers a home visit.
- Prior return is a yes/no field on the application. Any prior return counts, however old.

## Approach

1. Retrieve the criteria with rag_query — owner: feature-author
2. Implement requires_home_visit() in pawmatch/domain/home_visit.py, citing the policy in comments — owner: feature-author
3. Tests: one flag per rule, just under, at and just over 40 lb, one, two and three animals, a clear pass, and an invalid application — owner: pawmatch-test-writer
4. Re-query the policy; check the code for drift and for layer violations — owner: pawmatch-policy-reviewer
5. Run the stack with `scripts/start.sh` (`docker compose up --build` until the script exists), post one flagged application, read NOTES.md, decide to merge — owner: you

## Quality gates

- `uv run pytest` passes, the architecture test included, and `ruff check` is clean.
- The reviewer reports "no drift, no layer violations" with file:line references.
- `docker compose build` succeeds.

## Out of scope

- Notifying applicants. Changing the policy itself. Deploying. Authentication (not needed, decided 2026-11-23).

## Risks and open questions

- The policy may change while this is in flight. The reviewer's re-query is the guard.
- rag_query returns only the first 400 characters of each policy file. The policy is already
  438 characters, so the criteria fit but its closing sentence is cut. Raise the limit before it grows.
