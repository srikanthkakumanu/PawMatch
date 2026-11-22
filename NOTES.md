# NOTES.md — Auto-flag applications needing a home visit

Why and evidence. The approach is in PLAN.md, the status is in TASK.md.

## Decisions

- 2026-08-07: "more than two animals" is `> 2`, not `>= 2`. The policy says "more than two", so exactly two is not flagged.
- 2026-08-07: keep the three rules as separate ifs in pawmatch/domain/home_visit.py so each can cite its own policy line.
- 2026-08-07: the rule stays in the domain. SubmitApplication calls it, and the route never sees it.
- 2026-11-23: the project needs start and stop scripts. They wrap the local Docker Compose stack only, because deploying is a human step.
- 2026-11-23: the stop script keeps the Postgres volume, so a routine stop cannot lose adoption applications.
- 2026-11-23: start/stop has its own draft plan, PLAN-start-stop.md, because PLAN.md covers the home-visit feature.
- 2026-11-23: TASK.md steps 1–4 and the Verify section were reset, because the repo has no code, tests or commits to support them.
- 2026-11-23: the test plan now covers just under, at and just over each threshold, as testing-rules.md requires.
- 2026-11-23: kennel safe intake applies the 80% ceiling to buildings available that week. The low-capacity warning uses safe intake, the more cautious reading.
- 2026-11-23: `kennel_capacity.py` now warns from safe intake, not end-of-week availability, which could hide a full 80% ceiling.
- 2026-11-23: proposed a scaffold prerequisite (step 0) in PLAN.md, because the plan's gates need code that does not exist. It was later approved and implemented the same day.
- 2026-11-23: no authentication is needed. It is out of scope for PLAN.md (project owner's decision).
- 2026-11-23: extra `.env` entries are ignored. The `api` service receives only `DATABASE_URL` and `PORT`.
- 2026-11-23: pytest is a uv dev dependency, and the standard test command is `uv run pytest`.
- 2026-11-23: the new stack uses Compose project `pawmatch-stack` and its own volume. The older `pawmatch_pgdata` volume holds 10 applications from an earlier app, with a different role and schema and no stored decisions, so it was left untouched.

## Agent reports (evidence)

- Main session, 2026-11-23: PROJECT.md acceptance check passed on a disposable Compose project: start twice, submit, stop twice, restart, decision still retrieved. Output and logs contained no password, `DATABASE_URL` or test PII. The API runs as non-root and receives only the documented variables.
- pawmatch-test-writer, 2026-11-23: added 17 tests in tests/test_home_visit.py. Main session re-ran `uv run pytest`: 32 passed. `ruff check` is clean.
- pawmatch-policy-reviewer, 2026-11-23: re-queried the policy and reported "no drift, no layer violations", citing pawmatch/domain/home_visit.py:16-26, pawmatch/interface/api.py:27-33 and pawmatch/main.py:3-6. Its query still used the 400-character limit, so it also read the policy file directly. Its missing trace comment on `DOG_SPECIES` was fixed. Negative weight is rejected for all animals, slightly stricter than PROJECT.md.
- pawmatch-policy-reviewer, 2026-11-23, after the fixed species list: re-queried the policy and reported "no drift, no layer violations", citing pawmatch/domain/home_visit.py:16-26 and pawmatch/domain/application.py:27-42. It found no way for a dog to bypass the rule except a person deliberately choosing `cat` or `other`. Main session: `uv run pytest` 42 passed, `ruff check` clean, and the running API returned 422 for "puppy", "dgo" and "German Shepherd".
- Main session, 2026-11-23: ran the real scripts with the local `.env`. Start and stop each succeeded twice. A 45 lb dog with no fenced yard returned `home_visit_required`, and the decision survived a stop and restart. One test row remains in `pawmatch-stack_pgdata`, ID 7eb4c673-14c7-4718-b509-be825be1671b, named "VERIFY TEST - NOT A REAL APPLICANT". No credentials, `DATABASE_URL` or test PII appeared in output or logs.

Main session, 2026-11-23: rag_query("which applications require a mandatory home visit?") returned from policies/screening-policy.md:

> - The applicant has no fenced yard and is adopting a dog over 40 lbs.
> - The applicant has any prior return of an adopted animal to this shelter.
> - The applicant is adopting more than two animals in a single application.

Unverified as of 2026-11-23: the earlier reports below have no matching code, tests or commits in the repo. Do not rely on them.

- feature-author: rag_query("which applications require a mandatory home visit?") returned the three criteria from policies/screening-policy.md.
- pawmatch-test-writer: added 7 tests (one flag per rule, the 40 lb and two-animal boundaries, a clear pass, an invalid application). `pytest tests/test_home_visit.py`: 7 passed.
- pawmatch-policy-reviewer: re-ran rag_query. Code matches the policy. No PII in logs. No layer imports outward. No drift.

## Open questions

- What should happen to the 10 applications in the older `pawmatch_pgdata` volume? — owner: adoptions manager

Answered 2026-11-23 by the adoptions manager or their delegate:

- Should a prior return from many years ago still count? Yes, any prior return counts.
- How is a prior return identified? By the applicant's answer, recorded as a yes/no field on the application.
- Does the 40 lb rule apply when any one dog in a multi-dog application is over 40 lbs? Yes, any one dog.
- Should species be a fixed list? Yes: `dog`, `cat` or `other`. Puppies and all breeds are entered as `dog`, and anything else is rejected, because free text let a 45 lb "puppy" or "German Shepherd" skip the 40 lb rule.

## Verify (human checkpoint)

- Acceptance criteria met? verify.
- Security or architecture concerns? Not required.
- Decision: pending.
