# PLAN-start-stop.md — Local start and stop scripts

Status: approved 2026-11-23 by the adoptions manager or their delegate. The main session performs feature-author's steps, by the same approval.

## Objective

Anyone working on PawMatch can start and stop the local Docker Compose stack with one
command, without losing adoption applications.

## Constraints

- Requirements: "Operational requirements" in PROJECT.md.
- Local stack only. Deploying remains a human step.
- The stop script never removes the Postgres volume.

## Prerequisites

- Dockerfile and docker-compose.yml exist at the repo root.

## Approach

1. Add `scripts/start.sh` — owner: feature-author
2. Add `scripts/stop.sh` — owner: feature-author
3. Run the PROJECT.md acceptance check — owner: you

## Quality gates

- `docker compose build` succeeds.
- Running either script twice in a row succeeds.
- An application's decision can still be retrieved after a stop and restart.
- Script output contains no credentials, `DATABASE_URL` or applicant PII.

## Out of scope

- Deleting local data. Deploying. Changing screening behavior.
