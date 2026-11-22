# PawMatch API reference

Screening never approves or rejects an application. A person always makes that call.

## POST /applications

Records an application and screens it.

```json
{
  "applicant_name": "Example Applicant",
  "address": "1 Example Street",
  "income": "50000",
  "has_fenced_yard": false,
  "has_prior_return": false,
  "animals": [{ "species": "dog", "weight_lbs": 45 }]
}
```

`income` is optional. `species` must be `dog`, `cat` or `other`, and puppies and all breeds are
entered as `dog`. `weight_lbs` is required for dogs and optional for other animals.

`201` response:

```json
{ "application_id": "<uuid>", "decision": "home_visit_required" }
```

`decision` is `home_visit_required` or `standard_review`.

## GET /applications/{application_id}/decision

Returns the same body as the `201` response, and never returns applicant details.

## GET /health

Returns `200 {"status": "ok"}` when the API can reach Postgres.

## Errors

| Status | Meaning |
| ------ | ------- |
| `404`  | The application does not exist. |
| `422`  | The request is invalid. Submitted values are never echoed. |
| `503`  | The application store is unavailable. |
