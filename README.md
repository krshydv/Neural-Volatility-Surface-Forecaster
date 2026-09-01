# HERMES FORECAST : Neural Volatility Surface Forecaster

A quantitative finance platform for **implied volatility surface construction, neural forecasting, options analytics, and market regime detection**.

The platform combines a real FastAPI/PostgreSQL backend, a from-scratch neural forecasting engine, options analytics, and a Next.js frontend — with an explicit, honest record of what's been executed and verified versus written-but-unverified at every stage (see `docs/PROJECT_STATE.md`).

---

# Overview

This project models and forecasts implied volatility surfaces using a from-scratch neural forecasting engine, closed-form and numerical quantitative finance techniques, and options analytics.

The system integrates:

- Volatility surface construction pipelines
- A from-scratch NumPy LSTM forecasting model (plus an MLP baseline)
- Options chain analytics
- Market regime detection (from-scratch k-means)
- A real, JWT-authenticated backend API
- An interactive Next.js frontend dashboard
- Docker Compose deployment, with Kubernetes manifests written but not yet applied to a real cluster

The objective is a quantitative research platform for volatility modeling and options analytics, built incrementally and documented honestly at each step rather than presented as a finished institutional product.

---

# Core Features

## Quantitative Finance Engine

- Implied volatility computation (Newton-Raphson with a Brent fallback)
- Black-Scholes pricing and inversion
- Volatility surface generation and interpolation
- Full Greeks computation (delta, gamma, theta, vega, rho)
- Options chain analytics
- Smile and skew analysis
- Historical volatility analytics
- Risk exposure metrics

---

## Forecasting

- From-scratch NumPy LSTM (manual forward/backward pass, full BPTT)
- MLP baseline kept selectable for comparison
- Autoregressive multi-day volatility forecasting with confidence bounds
- Celery-based async training-job queue, Redis as broker

---

## Volatility Analytics

- Surface interpolation
- Strike-expiry mapping
- Market regime detection (from-scratch k-means over rolling realized volatility)
- Scenario analysis (shocked-chain repricing through the same tested Black-Scholes engine)

---

## Frontend Dashboard

- Interactive volatility surface visualization
- Options chain analytics
- Multi-page Next.js frontend (Dashboard, Markets, Research, Analytics)
- Forecast Lab with model selector (LSTM / MLP)
- Model Experiments run log
- Command palette (⌘K)

---

## Backend Infrastructure

- FastAPI backend services
- REST API architecture
- Real JWT authentication (access + refresh tokens), plus optional Google OAuth login
- Redis integration (rate limiting, Celery broker)
- PostgreSQL integration via SQLAlchemy 2.0 + Alembic
- Client-persisted run log for forecast experiments (not a full experiment-tracking system — no artifact storage or versioning)

---

## Infrastructure & Deployment

- Docker Compose orchestration (7 services: postgres, redis, api, celery worker, web, prometheus, grafana) — verified to build and start cleanly
- Kubernetes manifests (namespace, Deployments/StatefulSets, HPA, PodDisruptionBudgets, NetworkPolicy, ingress) — written, **not yet applied to a real cluster**
- Prometheus monitoring (`/metrics` endpoint, scrape config)
- Grafana dashboards (request rate, p95 latency, 429 rate)
- Postgres/Redis healthchecks
- `infra/nginx/` scaffolding present, not built out

---

# Tech Stack

## Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
- Celery

---

## Quant / ML

- NumPy
- SciPy
- From-scratch LSTM and MLP (no PyTorch dependency)

---

## Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- Vitest + Testing Library

---

## DevOps & Infrastructure

- Docker
- Kubernetes (manifests written, unverified against a real cluster)
- Prometheus
- Grafana

---

# Architecture

```text
Next.js frontend (apps/web)
        │  REST, JWT bearer auth
        ▼
FastAPI backend (apps/api)
 ┌──────┼──────────┐
 ▼      ▼          ▼
Redis  PostgreSQL  Celery worker
 │                  │
 ▼                  ▼
Rate limiter /   Async forecast
Job broker       training jobs
```

---

# Project Structure

```text
volaris/
│
├── apps/
│   ├── api/
│   │   ├── app/
│   │   │   ├── api/v1/
│   │   │   ├── quant/
│   │   │   ├── forecasting/
│   │   │   ├── analytics/
│   │   │   ├── workers/
│   │   │   ├── models/
│   │   │   ├── repositories/
│   │   │   ├── services/
│   │   │   └── core/
│   │   ├── scripts/
│   │   └── tests/
│   │
│   └── web/
│       ├── app/
│       ├── components/
│       ├── lib/
│       └── public/
│
├── infrastructure/
│   ├── kubernetes/
│   ├── nginx/
│   ├── prometheus/
│   └── grafana/
│
├── scripts/
│   └── seed_demo_data.py
├── datasets/
├── notebooks/
├── docker-compose.yml
├── README.md
└── .env.example
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/krshydv/Neural-Volatility-Surface-Forecaster.git
```

## Move Into Project Directory

```bash
cd Neural-Volatility-Surface-Forecaster
```

## Start Full Stack

```bash
docker compose up --build
```

## Optional: Seed Demo Data

```bash
docker compose exec api python scripts/seed_demo_data.py
```

Creates a `demo@volaris.ai` login with a workspace pre-populated with 18 real forecast runs (password printed to stdout).

---

# Services

| Service | Port |
|---|---|
| Frontend | 3000 |
| Backend API | 8000 |
| Grafana | 3001 |
| Prometheus | 9090 |
| PostgreSQL | 5432 |
| Redis | 6379 |

---

# Project Status

## Verified end-to-end (live HTTP against a real Postgres, 123+ backend tests)

- Auth, workspaces, options chain, volatility surface
- Greeks, quant pricing
- Regime detection, scenario lab, risk analytics

## Verified standalone (real execution, not just written)

- LSTM forecasting model and the full forecast pipeline

## Verified via an actual Docker build

- Web container compiles and starts cleanly under the current UI

## Written and internally consistent

- Redis-backed rate limiting fallback logic
- Prometheus metrics middleware
- Celery training-job queue
- Google OAuth login flow
- All Kubernetes manifests

---

# Honest Scope

This is not presented as an institutional or production-grade system. It's a real, working quantitative research platform with a genuine backend, real tests, and a documented, session-by-session record — in `docs/PROJECT_STATE.md` — of exactly what has and hasn't been proven to work, including bugs that were hit and fixed along the way (a missing dependency, a lockfile mismatch, a Docker volume misconfiguration). No claim in this README goes beyond what's actually demonstrable in the codebase.

---

# Monitoring & Observability

- Prometheus metrics endpoint (`/metrics`)
- Grafana dashboards (request rate, p95 latency, 429 rate)
- Postgres/Redis healthchecks
- Kubernetes readiness/liveness probes (in the unverified manifests)

---

# Future Expansion Goals

- Live options market data integration
- Multi-asset volatility forecasting
- A larger/framework-backed model (PyTorch) alongside the current from-scratch LSTM
- Real experiment tracking with model versioning
- Apply and verify the Kubernetes manifests against a real cluster
- Frontend test coverage for the analytics/research pages

---

# License

This project is licensed under the MIT License.

---

# Author

## KRISH YADAV

Built as a full-stack quantitative finance research platform focused on implied volatility forecasting, options analytics, and honest, verifiable engineering documentation.
