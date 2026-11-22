---
paths:
  - "pawmatch/domain/**"
---
# Domain layer rules

- Plain Python: no imports from fastapi, pydantic, psycopg or any other layer.
- An entity cannot exist in an invalid state: validate in __post_init__.
- Every screening rule cites its line in policies/screening-policy.md in a comment.
