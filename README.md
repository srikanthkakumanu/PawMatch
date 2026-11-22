# PawMatch

PawMatch is a REST API that lets animal shelter staff record adoption applications and screen
them consistently before approval. It is used by the intake desk and the adoptions manager.

Screening decides one thing: whether an application needs a **mandatory home visit**. It never
approves or rejects an adoption. A person always makes that call.

## Contents

- [Screening rules](#screening-rules)
- [Quick start](#quick-start)
- [API](#api)
- [Architecture](#architecture)
- [Development](#development)
- [Privacy and security](#privacy-and-security)
- [Deployment](#deployment)
- [Kennel capacity planning](#kennel-capacity-planning)
- [Agentic workflow](#agentic-workflow)
- [Project documents](#project-documents)

## Screening rules

The source of truth is [`policies/screening-policy.md`](policies/screening-policy.md), which the
adoptions manager owns. An application gets `home_visit_required` if **any** of these match:

| Criterion | How it is applied |
| --- | --- |
| No fenced yard and a dog over 40 lbs | Any one dog counts. Exactly 40 lbs does not match. |
| Any prior return to this shelter | A yes/no answer from the applicant. Any return counts, however old. |
| More than two animals in one application | Exactly two does not match. |

Every other application gets `standard_review`.

To change a criterion, the adoptions manager edits the policy file first. The code in
[`pawmatch/domain/home_visit.py`](pawmatch/domain/home_visit.py) then follows it, with a comment
citing the policy line.

An application is rejected if it has a blank applicant name, no animals, a negative or non-finite
weight, a dog with no weight, or a species other than `dog`, `cat` or `other`. Puppies and all
breeds are entered as `dog`, so a free-text value cannot skip the 40 lb rule.

## Quick start

You need [Docker](https://docs.docker.com/get-docker/) with Docker Compose.

**1. Create a `.env` file in the repo root.** It is ignored by git and never copied into the image.

```dotenv
POSTGRES_PASSWORD=choose-a-local-password
PORT=8000
DB_PORT=5433
```

The password is placed in a connection URL, so URL-encode any reserved characters in it.

**2. Start the stack.** The script builds the images and returns once the API and Postgres are ready.

```bash
./scripts/start.sh
```

**3. Submit an application.**

```bash
curl -s -X POST http://127.0.0.1:8000/applications \
  -H 'Content-Type: application/json' \
  -d '{
    "applicant_name": "Example Applicant",
    "address": "1 Example Street",
    "income": "50000",
    "has_fenced_yard": false,
    "has_prior_return": false,
    "animals": [{ "species": "dog", "weight_lbs": 45 }]
  }'
```

```json
{ "application_id": "<uuid>", "decision": "home_visit_required" }
```

**4. Read the decision back.**

```bash
curl -s http://127.0.0.1:8000/applications/<uuid>/decision
```

**5. Stop the stack.** Containers and the network are removed. The Postgres volume is kept, so
applications survive a restart.

```bash
./scripts/stop.sh
```

Both scripts work from any directory and are safe to run twice.

### Environment variables

| Variable | Used by | Purpose |
| --- | --- | --- |
| `POSTGRES_PASSWORD` | Local Compose | Secret. Password for the Compose Postgres service. |
| `PORT` | API | Port the API listens on. |
| `DB_PORT` | Local Compose | Host port for Postgres. |
| `DATABASE_URL` | API | Secret. Postgres connection string. Compose builds it for you locally. |

Compose publishes both ports on `127.0.0.1` only.

## API

Interactive docs are served at `/docs` while the API is running. The full reference is in
[`docs/api-reference.md`](docs/api-reference.md).

| Method | Path | Purpose | Success |
| --- | --- | --- | --- |
| `POST` | `/applications` | Record and screen an application | `201` |
| `GET` | `/applications/{application_id}/decision` | Read a stored decision | `200` |
| `GET` | `/health` | Check that the API can reach Postgres | `200` |

Application and decision responses contain only `application_id` and `decision`.

| Error | Meaning |
| --- | --- |
| `404` | The application does not exist. |
| `422` | The request is invalid. Submitted values are never echoed. |
| `503` | The application store is unavailable. |

## Architecture

PawMatch uses Domain-Driven Design with four layers. Dependencies point inward only.

```mermaid
flowchart LR
    main["main.py<br/>composition root"] --> interface
    main --> infrastructure
    interface["interface<br/>FastAPI routes, schemas, HTTP errors"] --> application
    infrastructure["infrastructure<br/>Postgres adapter, config"] --> application
    application["application<br/>use cases, repository port"] --> domain
    domain["domain<br/>entities, screening rule"]
```

| Layer | Responsibility | Key files |
| --- | --- | --- |
| `domain/` | Entities and screening rules. Plain Python only. | `application.py`, `home_visit.py`, `decision.py` |
| `application/` | `SubmitApplication`, `GetDecision` and the `ApplicationRepository` port. | `use_cases.py`, `ports.py` |
| `infrastructure/` | The only SQL in the project, plus environment config. | `postgres_repository.py`, `config.py` |
| `interface/` | Routes, request models and the mapping of errors to HTTP. | `api.py`, `schemas.py` |
| `main.py` | The only place an adapter is wired to a port. | `main.py` |

`tests/test_architecture.py` fails the build if a layer imports outward, or if `domain/` or
`application/` imports a framework or database driver.

**Stack:** Python 3.15, FastAPI, Pydantic, psycopg, PostgreSQL 17, uv, Docker Compose and Render.

### Repository layout

```text
pawmatch/            Application code, in the four layers above
policies/            Screening policy (source of truth)
tests/               Unit, API and architecture tests
docs/                API reference
scripts/             start.sh and stop.sh for the local stack
tools/               policy-rag MCP server
.claude/             Agents, path-scoped rules and the kennel capacity skill
Dockerfile           Multi-stage image that runs as a non-root user
docker-compose.yml   Local stack: api + db
render.yaml          Production service definition
```

## Development

You need [uv](https://docs.astral.sh/uv/). Tests fake the repository port, so they do not need
Postgres or Docker.

```bash
uv sync                          # Install dependencies
uv run pytest                    # Run all tests
uv run pytest -k home_visit      # Run only the screening rule tests
uv run ruff check                # Lint
uv run ruff format               # Format
```

To run the API outside Docker against the Compose database:

```bash
set -a; source .env; set +a
docker compose up -d db
DATABASE_URL="postgresql://postgres:${POSTGRES_PASSWORD}@localhost:${DB_PORT}/pawmatch" \
  uv run uvicorn pawmatch.main:app --reload --port "$PORT"
```

After changing dependencies or the `Dockerfile`, run `docker compose build`.

### Conventions

- Business rules live in `domain/`, never in a route handler or SQL query.
- Every screening rule and threshold has a comment citing its line in the policy.
- New screening rules need tests just under, at and just over any threshold.
- New endpoints need a Pydantic request model and an entry in `docs/api-reference.md`.
- Every function has type hints.
- Commits follow [Conventional Commits](https://www.conventionalcommits.org/).

## Privacy and security

- Applicant name, address and income never appear in logs, error messages or `GET` responses.
- One applicant's data is never exposed in another applicant's response.
- Application IDs are random UUIDs.
- Secrets come from the environment only, and the Docker build context is an explicit allowlist.
- The container runs as a non-root user.

> **The API has no authentication.** This was a deliberate project decision. Anyone who can reach
> the API can submit applications, and anyone with an application ID can read its decision, so
> account for this when choosing where the service is exposed.

## Deployment

Production runs on [Render](https://render.com/) from [`render.yaml`](render.yaml), using the
Docker image. Set `DATABASE_URL` as a secret in Render. Auto-deploy is off.

**Deploying is always a human step, after verification.** Agents and the local scripts never deploy.

## Kennel capacity planning

A separate Claude Code skill helps the intake desk work out how many animals it can safely take in
this week. It is not part of the API and never affects screening.

```bash
python3 .claude/skills/kennel-capacity-check/scripts/kennel_capacity.py \
  --total-kennels 40 --occupied-kennels 33 --expected-adoptions-this-week 4
```

Safe intake is `max(0, floor(total × 0.8) − (occupied − expected adoptions))`, which is 3 in this
example. The 80% ceiling reserves kennels for medical holds, and the script warns at 2 or fewer.
Count only buildings available that week, as listed in the
[kennel sizing notes](.claude/skills/kennel-capacity-check/reference/kennel-sizing-notes.md).

## Agentic workflow

PawMatch is built with an agentic engineering approach, using Claude Code with human checkpoints.

| Component | Role |
| --- | --- |
| `policy-rag` MCP server | Answers from the policy files, so criteria are never taken from memory. |
| `pawmatch-test-writer` agent | Writes boundary-case tests, and edits only `tests/`. |
| `pawmatch-policy-reviewer` agent | Read-only check for PII leaks, policy drift and layer violations. |
| `.claude/rules/` | Rules for the domain, API and test code, applied by path. |

| Decision | Owner |
| --- | --- |
| Screening criteria | Adoptions manager, by editing the policy file |
| Merging a screening change, and any deployment | A human, at Verify |
| Extra tests and policy-drift reports | Agents |

## Project documents

| File | Contents |
| --- | --- |
| [`PROJECT.md`](PROJECT.md) | Purpose, domain model, operational requirements and glossary |
| [`CLAUDE.md`](CLAUDE.md) | Architecture rules and conventions for agents |
| [`PLAN.md`](PLAN.md) | Approved plan for the home-visit feature |
| [`PLAN-start-stop.md`](PLAN-start-stop.md) | Approved plan for the local scripts |
| [`TASK.md`](TASK.md) | Status board |
| [`NOTES.md`](NOTES.md) | Why-decisions and agent evidence |
