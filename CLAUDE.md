# CLAUDE.md — PawMatch

## Project context

@PROJECT.md

## Architecture

Python 3.15 / FastAPI REST API, uv, Pydantic modules. Postgres for adoption applications.
Domain-Driven Design in four layers under pawmatch/. Dependencies point inward only:

Note: This project is implemented using Agentic Engineering Approach.

- domain/          entities and screening rules: AdoptionApplication, requires_home_visit.
  No imports from other layers, and no framework or database driver.
- application/     use cases (SubmitApplication, GetDecision) and the ApplicationRepository port.
  Imports domain only.
- infrastructure/  adapters: PostgresApplicationRepository (the only SQL) and config.
- interface/       FastAPI routes, request models, and the mapping of errors to HTTP.
- main.py          composition root: the only place an adapter is wired to a port.
  Packaged as a Docker image. Docker Compose locally, Render in production.

## Conventions

- Applicant PII (name, address, income) never appears in logs, error messages or GET responses.
- Screening decisions must always trace back to a documented policy — no undocumented judgment calls in code.
- Business rules live in domain/. No rule in a route handler or a SQL query.
- Tests: pytest. Run `uv run pytest`. Fake the ApplicationRepository port (tests/conftest.py).
  tests/test_architecture.py enforces the layer rules: keep it green.
- Type hints on every function; `ruff check` and `ruff format` before each commit.
- Commits: Conventional Commits.

## Containers

- Dockerfile, docker-compose.yml (api + postgres) and render.yaml live at the repo root.
- `scripts/start.sh` and `scripts/stop.sh` are the standard way to run the local stack (requirements in PROJECT.md).
  `scripts/stop.sh` must never remove the Postgres volume: no `docker compose down -v`.
  The image runs as a non-root user.
- Config comes from environment variables only (DATABASE_URL, PORT, and locally DB_PORT, POSTGRES_PASSWORD; see PROJECT.md). Never COPY a .env file or a credential into the image.
- After changing dependencies or the Dockerfile, run `docker compose build` before saying you are done.
- Never deploy. Deploying is a human step, after Verify.

## Do not

- Do not expose one applicant's data in another applicant's API response, even partially.
- Do not hardcode screening thresholds without a comment tracing them to the policy doc they came from.
- Do not import fastapi, pydantic or psycopg from domain/ or application/.

## Tooling

- Team's Claude Code setup ships as one plugin: `/plugin install pawmatch-toolkit@shelter-platform-marketplace`.
- PLAN.md needs the policy-rag server and the feature-author agent. If either is unavailable, stop and report it. Never take screening criteria from memory.

## Working files

- Read the plan for your task before starting: PLAN.md (home-visit feature) or PLAN-start-stop.md (local scripts).
  Do not implement a plan whose status is draft or re-approval pending.
- TASK.md is the status board. Only the main session edits it; subagents report, they do not edit.
- Record why-decisions and agent evidence in NOTES.md.
