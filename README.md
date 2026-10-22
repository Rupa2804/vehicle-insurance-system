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

```text
vehicle-insurance-system/
├── app/
│   ├── api/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── repositories/
│   ├── database/
│   ├── auth/
│   └── config/
├── tests/
├── docs/
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── index.html
│   └── vite.config.ts
├── .env.example
├── .gitignore
├── requirements.txt
├── Dockerfile
└── README.md
```

## Run the API

In PowerShell, create and activate a virtual environment, install the backend
requirements, then copy the environment template if a local `.env` does not
already exist:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
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

## Role-based access and web application

The API uses bearer-token authentication. Except for the health checks and
`POST /auth/login`, resource routes require a valid access token. An initial
administrator must be created privately with `python -m app.auth.create_admin`;
administrators provision all other accounts through `POST /auth/users`. There
is no public user-registration endpoint. Login requires selecting the
account's assigned role; the API rejects a role that does not match the
provisioned account and derives permissions from the database account, not the
selected value.

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

Customers and surveyors must be linked to their existing customer/surveyor
record when their account is provisioned. To add a surveyor, an administrator
creates the surveyor profile in **Surveyors**, then creates the login account
in **User access** and selects that profile. The web application is a React,
TypeScript, and Vite client, with all frontend source and build configuration
grouped under `frontend/`:

```powershell
Set-Location .\frontend
Copy-Item .env.example .env.local
npm install
npm run dev
```

Set `VITE_API_BASE_URL` in `frontend/.env.local` when the API is hosted at a
different address; the default is `http://localhost:8000`. See
[`docs/api-documentation.md`](docs/api-documentation.md) for endpoint status
codes, authentication, and error responses.

## Deploy to Vercel

Keep the Vercel project root set to the repository root. The root
[`vercel.json`](vercel.json) builds the frontend during deployment, and
FastAPI serves the built single-page application at `/`. On Vercel, API routes
are available under `/api`, and the frontend uses that same deployment
origin. No `VITE_API_BASE_URL` setting is needed unless the API is hosted
separately.

Configure the backend's required environment variables in the Vercel project
settings, including a strong `JWT_SECRET_KEY` and a production database URL.
Provision the initial administrator privately after deployment.
