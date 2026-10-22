# Vehicle Insurance Claim Management System

A backend system for managing the complete vehicle insurance claim process, from accident and policy verification to claim settlement and payment.

## Features

- Customer management
- Vehicle management
- Insurance policy management
- Accident and claim management
- Policy and coverage verification
- Vehicle inspection
- Damage assessment
- Claim status tracking and damage-assessment approval
- Settlement and payment management
- JWT authentication
- Role-based access control
- REST APIs

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- MongoDB
- JWT
- REST API
- Docker
- Pytest

## Prerequisites

Make sure you have the following installed:

- Python 3.x
- PostgreSQL
- MongoDB
- Git
- Docker (optional)


## Project Structure

The repository root contains exactly these three project items:

```text
vehicle-insurance-system/
├── backend/
│   ├── app/
│   ├── tests/
│   ├── docs/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── vercel.json
├── frontend/
│   ├── src/
│   ├── package.json
│   └── package-lock.json
└── README.md
```

## Run the API

In PowerShell, create and activate a virtual environment in `backend/`, install
the backend requirements, and create a local environment file:

```powershell
Set-Location .\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Set a strong private `JWT_SECRET_KEY`, configure `DATABASE_URL` for the chosen
database, and set `CORS_ORIGINS` to the exact browser origins that should use
the API. Start the service in one terminal:

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

In a second terminal, create the initial administrator:

```powershell
python -m app.auth.create_admin
```

The API creates missing tables at startup. The default CORS allowlist includes
the local Vite origins (`localhost:5173` and `127.0.0.1:5173`); production
deployments should replace these with their trusted frontend origins.
The initial administrator can be provisioned against the same database with
`python -m app.auth.create_admin` from the `backend/` directory.

## Role-based access and web application

The API uses bearer-token authentication. Health checks, `POST /auth/login`,
and `POST /auth/register` are public. Customers can create their own account
from the login page or Swagger UI; registration creates a linked customer
profile and account in one transaction, then signs the customer in. The login
page requires selecting the account's assigned role, which the API verifies
against the database. A selected role never grants additional permissions.

Employee and privileged accounts remain administrator-provisioned through
`POST /auth/users`. This keeps user provisioning and the sensitive ADMIN,
CLAIMS_OFFICER, SURVEYOR, FINANCE, and MANAGER roles under administrative
control. AGENT accounts can be created by an administrator and can create
customer profiles directly through `POST /customers/` in Swagger or the web
application.

| Role | Access |
| --- | --- |
| CUSTOMER | Role dashboard for own claims and records; report own accidents, submit claims, and track claim, settlement, and payment progress. |
| AGENT | Role dashboard for customer assistance; create customer profiles, manage vehicle and policy records, assist with accident reporting, and submit claims. |
| CLAIMS_OFFICER | Role dashboard for claim review; verify and update claims, coordinate inspections, manage damage assessments, and approve assessment costs. |
| SURVEYOR | Role dashboard for assigned work; view assigned claims and inspections, update inspection findings, and create/update damage assessments for assigned claims. |
| FINANCE | Role dashboard for financial work; read approved claims, create/update settlements only for approved claims, process payments, and view financial reports. |
| MANAGER | Read-only role dashboard for operational and financial oversight, with access to reports but no write operations or user provisioning. |
| ADMIN | Administrative dashboard for user provisioning and system oversight; create accounts for all roles, create surveyor profiles, and access administrative operations. |

Each role lands on a dashboard with metrics and quick links tailored to its workflow. Frontend routes and controls follow the backend's explicit per-role allowlist; the API remains authoritative and rejects unauthorized requests even when called directly.

Customer self-registration creates the customer profile and account together.
To add a surveyor, an administrator creates the surveyor profile in
**Surveyors**, then creates the login account in **User access** and selects
that profile. The web application is a React,
TypeScript, and Vite client, with all frontend source and build configuration
grouped under `frontend/`:

```powershell
Set-Location .\frontend
npm ci
npm run dev
```

Set `VITE_API_BASE_URL` in `frontend/.env.local` when the API is hosted at a
different address; the default is `http://localhost:8000`. See
[`backend/docs/api-documentation.md`](backend/docs/api-documentation.md) for endpoint status
codes, authentication, and error responses.

## Deploy to Vercel

Set the Vercel project root directory to `backend/`. The
[`backend/vercel.json`](backend/vercel.json) build command installs and builds
the frontend, then copies its static output into the backend bundle. The FastAPI
app serves the single-page application at `/`; API routes use the `/api`
prefix, so the frontend uses the same deployment origin.

Configure the backend's required environment variables in the Vercel project
settings: set a strong private `JWT_SECRET_KEY`, a persistent managed
PostgreSQL `DATABASE_URL`, and `CORS_ORIGINS` to the deployed frontend origin.
Vercel's filesystem is not persistent; the application fails startup rather
than silently falling back to SQLite when deployed there. Vercel builds the
frontend from `frontend/package-lock.json` and detects the FastAPI entrypoint
at `backend/app/main.py`. Provision the initial administrator privately after
deployment with `python -m app.auth.create_admin` using the same `DATABASE_URL`
from a secure environment.

## Build and run with Docker

From the repository root, build the image using the root as the build context
and the Dockerfile under `backend/`:

```powershell
docker build -f backend/Dockerfile -t vehicle-insurance-system .
docker run --rm -p 8000:8000 `
  -e DATABASE_URL="postgresql+psycopg://user:password@host:5432/vehicle_insurance_db" `
  -e JWT_SECRET_KEY="replace-with-a-private-secret-of-at-least-32-characters" `
  -e CORS_ORIGINS="http://localhost:5173" `
  vehicle-insurance-system
```

The image builds the frontend, runs FastAPI as a non-root user, and includes a
database-backed health check at `/health/ready`. Supply a managed persistent
database and private secrets in production, and put the service behind HTTPS.
