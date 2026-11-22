
# PROJECT.md — PawMatch

## Purpose

Lets shelter staff record adoption applications and screen them consistently
before approval. Used by the intake desk and the adoptions manager.

## Sources of truth

- Which applications need a home visit → policies/screening-policy.md, via the policy-rag server
- Kennel capacity by building → .claude/skills/kennel-capacity-check/reference/kennel-sizing-notes.md
  This supports intake-desk planning through a Claude skill. It is not part of the API and never affects screening.

## Who decides what

- Screening criteria: the adoptions manager, by editing the policy file. Agents never invent criteria.
- Merging a screening change, and any deployment: a human, at Verify.
- Extra tests and policy-drift reports: agents.

## Domain model

- AdoptionApplication (entity): one application. Cannot exist with a blank name, fewer than one animal, a negative dog weight, or a species other than dog, cat or other. Puppies and all breeds are entered as dog.
- requires_home_visit (domain rule): decides from the application alone whether a home visit is mandatory.
- ScreeningDecision: "home_visit_required" or "standard_review".

## Operational requirements

### Local start and stop scripts

The project provides `scripts/start.sh` and `scripts/stop.sh`, so anyone can run the
local Docker Compose stack (api + postgres) with one command.

`scripts/start.sh` must:

- Build the images and start the stack in the background.
- Exit 0 only once the api and postgres are ready to serve, and print the API's local URL.
- Succeed without duplicating anything if the stack is already running.

`scripts/stop.sh` must:

- Stop and remove the stack's containers and network.
- Keep the Postgres volume, so adoption applications survive a stop and restart.
- Succeed if the stack is already stopped.

Both scripts must:

- Work when called from any directory.
- Exit non-zero with a clear message if Docker is unavailable or a step fails.
- Take configuration from the environment variables listed below, with no hardcoded
  host ports or credentials.
- Never print credentials, `DATABASE_URL` or applicant PII.
- Act on the local stack only: never deploy and never touch Render.

Acceptance check: start the stack, submit an application, stop, start again, and confirm
its decision can still be retrieved.

### Environment variables

- `DATABASE_URL` (secret): the API's Postgres connection string.
- `PORT`: the port the API listens on.
- `DB_PORT` (local only): the host port for the Compose Postgres service.
- `POSTGRES_PASSWORD` (secret, local only): the password for the Compose Postgres service.

Secrets come from the shell or an uncommitted local `.env`, and are never copied into the image.

## Out of scope, and why

- Approving or rejecting an adoption automatically — a person must always make that call.
- Notifying applicants — handled by the separate comms service.
- Deleting local data from the stop script — adoption records must not be lost by a routine stop.

## Glossary (ubiquitous language)

- "home visit": an in-person check required before approval when any screening criterion matches.
- "screening": applying the documented criteria to one application. It never approves anything.
- "decision": the outcome of screening, stored with the application.
