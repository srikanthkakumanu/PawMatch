#!/usr/bin/env bash
# Stops the local stack and removes its containers and network. Volumes are always kept.
set -euo pipefail

fail() {
  echo "stop.sh: $1" >&2
  exit 1
}

command -v docker >/dev/null 2>&1 || fail "Docker is not installed."
docker info >/dev/null 2>&1 || fail "Docker is not running."
docker compose version >/dev/null 2>&1 || fail "Docker Compose is not available."

project="${COMPOSE_PROJECT_NAME:-pawmatch-stack}"

# Addressing the project by name means stopping needs no secrets or port settings.
cd / || fail "cannot change directory."
docker compose --project-name "$project" down || fail "the stack could not be stopped."

echo "PawMatch stack stopped. The Postgres volume was kept."
