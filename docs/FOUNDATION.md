# NuclearGridRisk

PSA-inspired nuclear infrastructure risk simulation platform built with FastAPI, PostgreSQL/TimescaleDB, and NetworkX.

## Overview

NuclearGridRisk is a backend-driven simulation platform focused on modeling infrastructure dependencies, cascading failures, and operational risk propagation in synthetic civilian nuclear environments.

The project explores:
- infrastructure dependency graphs
- common-mode failures
- cascading disruptions
- time-series operational simulation
- probabilistic-inspired risk scoring

The system uses synthetic but operationally realistic datasets and does not model classified infrastructure.

---

## Tech Stack

- FastAPI
- PostgreSQL
- TimescaleDB
- SQLAlchemy 2.0
- Alembic
- NetworkX
- Loguru
- Pytest
- Ruff
- Docker

---

## Current Progress

### Completed
- FastAPI project initialization
- Structured logging setup
- PostgreSQL + TimescaleDB integration
- Alembic migrations
- Asset and dependency domain models
- Database health checks
- Testing infrastructure

### In Progress
- Asset CRUD APIs
- Dependency graph APIs
- Scenario engine

### Planned
- Common-mode failure simulation
- LOOP/SBO risk scoring
- Cascading failure propagation
- Time-series simulation engine
- Risk analytics APIs

---

## Architecture Direction

```text
FastAPI API Layer
        ↓
Service Layer
        ↓
Graph Simulation Engine (NetworkX)
        ↓
PostgreSQL + TimescaleDB

## Local Setup

Start database
```bash
docker compose up -d
```
Run API
```bash
uvicorn app.main:app --reload
```
Run tests
```bash
python -m pytest
```

## Disclaimer

This project uses synthetic infrastructure data for research and engineering simulation purposes only.
