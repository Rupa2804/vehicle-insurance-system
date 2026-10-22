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
is no public user-registration endpoint.

| Role | Access |
| --- | --- |
| CUSTOMER | Own profile, vehicles, policies, accidents, claims and related claim records; register vehicles and create accidents and claims. |
| AGENT | Manage customers, vehicles, policies and accidents; read claims and create claims. |
| CLAIMS_OFFICER | Read operational records; manage accidents, claims, inspections and assessments; review claims and approve/reject them after review; approve damage assessments; read reports. |
| SURVEYOR | Read assigned claims and inspections, update assigned inspections, and create/update assessments for assigned claims. |
| FINANCE | Read claims and assessments; manage settlements and process payments; read financial reports. |
| MANAGER | Read-only operational and financial oversight. |
| ADMIN | Full API access and user provisioning. |

Customers and surveyors must be linked to their existing customer/surveyor
record when their account is provisioned. The web application is a React,
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
