# Vehicle Insurance API

The application exposes interactive OpenAPI documentation at `/docs` and its
schema at `/openapi.json`.

## Authentication and role access

| Method and path | Access | Success |
| --- | --- | ---: |
| `POST /auth/login` | Public | 200 |
| `GET /auth/me` | Any authenticated user | 200 |
| `GET /auth/users` | ADMIN | 200 |
| `POST /auth/users` | ADMIN | 201 |

Use the returned `access_token` as `Authorization: Bearer <token>` on protected
resource requests. Create the first administrator with
`python -m app.auth.create_admin`; account provisioning is administrator-only.
There is no public registration route. Login requires the account's assigned
role; the server rejects a role mismatch and uses the provisioned database
account as the source of permissions. `CUSTOMER` accounts must link to a
customer record and `SURVEYOR` accounts to a surveyor record. These roles can
only access records within their ownership or survey assignment scope. Browser
clients must use an origin listed in the comma-separated `CORS_ORIGINS` setting.

| Role | Resource permissions |
| --- | --- |
| CUSTOMER | Own customer profile and related records; report own accidents, submit claims, and track claim/settlement/payment status. |
| AGENT | Manage customer profiles, vehicles, policies, and accident reports; assist with claim submission. |
| CLAIMS_OFFICER | Review and update claims, schedule inspections, and manage/approve damage assessments; cannot create user accounts or surveyor profiles. |
| SURVEYOR | Read assigned claims and inspections, update assigned inspections, and create/update assessments for assigned claims; cannot approve assessment costs. |
| FINANCE | Read approved claims, manage settlements only for approved claims, process payments, and read financial reports. |
| MANAGER | Read-only operational and financial oversight, with access to reports and no user provisioning. |
| ADMIN | All API operations and user provisioning. |

To provision a surveyor, an administrator first creates a surveyor profile with
`POST /surveyors/`, then creates a `SURVEYOR` account with the returned
`surveyor_id` using `POST /auth/users`. The UI provides the available profiles
as a selector when creating a surveyor account.

## Endpoints and success status codes

| Resource | Method and path | Success |
| --- | --- | ---: |
| Health | `GET /` | 200 |
| Health | `GET /health` | 200 |
| Customers | `POST /customers/` | 201 |
| Customers | `GET /customers/` | 200 |
| Customers | `GET /customers/{customer_id}` | 200 |
| Customers | `PATCH /customers/{customer_id}` | 200 |
| Vehicles | `POST /vehicles/` | 201 |
| Vehicles | `GET /vehicles/` | 200 |
| Vehicles | `GET /vehicles/{vehicle_id}` | 200 |
| Vehicles | `PATCH /vehicles/{vehicle_id}` | 200 |
| Policies | `POST /policies/` | 201 |
| Policies | `GET /policies/` | 200 |
| Policies | `GET /policies/{policy_id}` | 200 |
| Policies | `PATCH /policies/{policy_id}` | 200 |
| Accidents | `POST /accidents/` | 201 |
| Accidents | `GET /accidents/` | 200 |
| Accidents | `GET /accidents/{accident_id}` | 200 |
| Accidents | `PATCH /accidents/{accident_id}` | 200 |
| Accidents | `DELETE /accidents/{accident_id}` | 200 |
| Claims | `POST /claims/` | 201 |
| Claims | `GET /claims/` | 200 |
| Claims | `GET /claims/{claim_id}` | 200 |
| Claims | `PATCH /claims/{claim_id}` | 200 |
| Claims | `PATCH /claims/{claim_id}/status` | 200 |
| Claims | `DELETE /claims/{claim_id}` | 200 |
| Surveyors | `POST /surveyors/` | 201 |
| Surveyors | `GET /surveyors/` | 200 |
| Surveyors | `GET /surveyors/{surveyor_id}` | 200 |
| Surveyors | `PATCH /surveyors/{surveyor_id}` | 200 |
| Surveyors | `DELETE /surveyors/{surveyor_id}` | 200 |
| Inspections | `POST /inspections/` | 201 |
| Inspections | `GET /inspections/` | 200 |
| Inspections | `GET /inspections/{inspection_id}` | 200 |
| Inspections | `GET /inspections/claim/{claim_id}` | 200 |
| Inspections | `PATCH /inspections/{inspection_id}` | 200 |
| Inspections | `DELETE /inspections/{inspection_id}` | 200 |
| Damage assessments | `POST /damage-assessments/` | 201 |
| Damage assessments | `GET /damage-assessments/` | 200 |
| Damage assessments | `GET /damage-assessments/{assessment_id}` | 200 |
| Damage assessments | `GET /damage-assessments/claim/{claim_id}` | 200 |
| Damage assessments | `PATCH /damage-assessments/{assessment_id}` | 200 |
| Damage assessments | `POST /damage-assessments/{assessment_id}/approve` | 200 |
| Damage assessments | `DELETE /damage-assessments/{assessment_id}` | 200 |
| Settlements | `POST /settlements/` | 201 |
| Settlements | `GET /settlements/{settlement_id}` | 200 |
| Settlements | `GET /settlements/claim/{claim_id}` | 200 |
| Settlements | `PUT /settlements/{settlement_id}` | 200 |
| Settlements | `DELETE /settlements/{settlement_id}` | 200 |
| Payments | `POST /payments/` | 201 |
| Payments | `GET /payments/{payment_id}` | 200 |
| Payments | `GET /payments/settlement/{settlement_id}` | 200 |
| Payments | `POST /payments/{payment_id}/process` | 200 |
| Payments | `POST /payments/{payment_id}/fail` | 200 |
| Payments | `POST /payments/{payment_id}/refund` | 200 |
| Payments | `DELETE /payments/{payment_id}` | 200 |
| Reports | `GET /reports/settlements/summary` | 200 |
| Reports | `GET /reports/settlements/status` | 200 |
| Reports | `GET /reports/payments/summary` | 200 |
| Reports | `GET /reports/payments/status` | 200 |

Successful DELETE requests return a JSON message and therefore use `200 OK`
rather than `204 No Content`.

## Error status codes

| Status | Meaning |
| ---: | --- |
| 400 | The request is well-formed but violates a business validation rule. |
| 404 | The requested resource or required related resource does not exist. |
| 409 | A unique/database constraint conflicts with the request, or the requested state transition is not allowed. |
| 401 | Authentication is missing, invalid, or expired; login credentials are invalid. |
| 403 | The authenticated role is not allowed to perform the operation. |
| 422 | Request validation failed, including invalid fields or pagination parameters. |

List and report endpoints return `200 OK` with an empty collection or zero-valued
summary when there is no matching data. Pagination is supported on claims,
accidents, inspections, damage assessments, and surveyors with `skip` (default
`0`) and `limit` (default `100`, maximum `100`).

Claim status decisions use `PATCH /claims/{claim_id}/status`. A claim must move
from `SUBMITTED` to `UNDER_REVIEW` before it can be set to `APPROVED` or
`REJECTED`; decision states are terminal. The endpoint is available to
`CLAIMS_OFFICER` and `ADMIN`, and the officer makes the eligibility decision.
Damage-assessment approval is also available only to `CLAIMS_OFFICER` and
`ADMIN`; settlement records are created or updated by `FINANCE` or `ADMIN`
using the documented `POST` and `PUT` operations.