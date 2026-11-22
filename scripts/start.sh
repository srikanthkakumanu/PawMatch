#!/usr/bin/env bash
# Builds and starts the local stack, and returns once the api and postgres are ready.
set -euo pipefail

fail() {
  echo "start.sh: $1" >&2
  exit 1
}

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root" || fail "cannot enter the project directory."

command -v docker >/dev/null 2>&1 || fail "Docker is not installed."
docker info >/dev/null 2>&1 || fail "Docker is not running."
docker compose version >/dev/null 2>&1 || fail "Docker Compose is not available."

docker compose up --build --detach --wait --wait-timeout 180 ||
  fail "the stack did not become ready. Check it with: docker compose ps"

api_port="$(docker compose exec -T api printenv PORT)" || fail "could not read the API port."
address="$(docker compose port api "$api_port")" || fail "could not find the API address."

echo "PawMatch API is ready at http://${address}"
