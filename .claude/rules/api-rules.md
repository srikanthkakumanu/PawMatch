---
paths:
  - "pawmatch/interface/**"
  - "pawmatch/application/**"
---
# API & use-case layer rules

- Never return another applicant's data, even in error messages or logs.
- GET responses carry the decision only, never applicant details.
- Every screening decision must be traceable to a line in policies/screening-policy.md.
- New endpoints need a pydantic request model and an entry in docs/api-reference.md.
- Never return a domain entity directly: map it to a plain dict or response model.
- Domain and port errors become HTTP in pawmatch/interface/api.py, and nowhere else.
