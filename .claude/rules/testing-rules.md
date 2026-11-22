---
paths:
  - "tests/**"
---
# Testing rules

- Every new screening rule needs boundary-case tests: just under, at, and just over any threshold.
- Fake the ApplicationRepository port (tests/conftest.py). Unit tests never need a running Postgres.
- Run `uv run pytest` before proposing any diff as done; paste the summary line, not the full log.
- Flaky test allowance: zero.
