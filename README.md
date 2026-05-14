# NuclearGridRisk
## Overview

NuclearGridRisk is a graph-based infrastructure risk simulation platform designed to model cascading failures, dependency propagation, and resilience analysis within interconnected critical infrastructure environments.

The project is inspired by concepts from Probabilistic Safety Assessment (PSA), infrastructure dependency modeling, and systems engineering practices used in high-reliability environments.

Rather than focusing on reactor internals or classified operational systems, NuclearGridRisk simulates how failures in supporting infrastructure — such as substations, cooling systems, communication networks, backup generators, and transmission dependencies — can propagate across interconnected systems.

The platform is being developed as a production-style backend engineering project with emphasis on:

 - Graph intelligence
 - Failure propagation
 - Infrastructure dependency analysis
 - Simulation architecture
 - Time-series oriented risk modeling
 - Backend system design

## Core Goals
 - Model infrastructure assets and dependencies as directed graphs
 - Simulate cascading failures across interconnected systems
 - Analyze infrastructure fragility and bottlenecks
 - Explore resilience and redundancy strategies
 - Build a scalable simulation-oriented backend architecture
 - Apply production engineering practices to a complex domain problem

## Key Features
### Infrastructure Asset Registry

Manage infrastructure entities such as:

 - Power substations
 - Backup generators
 - Cooling systems
 - Sensor networks
 - Communication systems
 - Transmission lines
 - Control systems

Each asset includes metadata such as:

 - Asset type
 - Operational status
 - Criticality score
 - Location metadata
 - Simulation attributes

## Dependency Graph Modeling

Infrastructure relationships are represented as directed dependency graphs using NetworkX.

Supported dependency concepts include:

 - Physical dependencies
 - Communication dependencies
 - Power dependencies
 - Redundancy groups
 - Common-mode failure groups
 - Failure delay propagation

## Graph Intelligence Layer

The platform includes graph analysis capabilities for identifying:

 - Critical infrastructure hubs
 - Dependency bottlenecks
 - Upstream/downstream impact chains
 - Isolated infrastructure segments
 - Centrality-based risk indicators

Implemented / planned metrics include:

 - In-degree / out-degree analysis
 - Degree centrality
 - Betweenness centrality
 - Edge betweenness centrality
 - Dependency distribution analysis

## Failure Propagation Simulation

Simulation services model how infrastructure failures spread through dependency networks.

Current simulation capabilities include:

 - Immediate dependency impact analysis
 - Time-step based propagation modeling
 - Cascading dependency traversal
 - Delayed failure propagation
 - Redundancy-aware propagation logic

Planned future enhancements:

 - Probabilistic propagation
 - Dynamic recovery modeling
 - Scenario comparison engine
 - Monte Carlo simulation support
 - Risk heatmaps and visualization layers

## Technology Stack
### Backend
 - Python
 - FastAPI
 - SQLAlchemy
 - Pydantic v2
### Database
 - PostgreSQL
 - TimescaleDB (planned time-series simulation support)
 - Alembic migrations
### Graph & Simulation
 - NetworkX
### Tooling & Infrastructure
 - Docker Compose
 - Pytest
 - Ruff
 - Loguru

## Architecture Philosophy

NuclearGridRisk is intentionally designed using production-style backend engineering principles.

Key design priorities:

 - Modular service architecture
 - Separation of concerns
 - Test-driven development
 - Migration-driven database management
 - Simulation-oriented extensibility
 - Scalable graph processing patterns
 - Clean API versioning

## API Structure
```
/api/v1/assets
/api/v1/dependencies
/api/v1/graph
/api/v1/failure-simulation
/api/health
```

## Example Simulation Concepts

The platform explores concepts such as:

 - Loss of Offsite Power (LOOP/LOSP)
 - Station blackout propagation
 - Cascading infrastructure disruption
 - Redundancy collapse
 - Common-mode failures
 - Dependency-driven systemic risk

These concepts are implemented as engineering simulations using synthetic or abstracted infrastructure models.

## Project Status

Current development progress includes:

 - FastAPI backend setup
 - PostgreSQL integration
 - SQLAlchemy models
 - Alembic migration system
 - Asset & dependency CRUD APIs
 - Graph builder service
 - Network analysis layer
 - Traversal APIs
 - Failure propagation foundation
 - Automated testing setup
 - Structured logging integration

The project is currently under active development.

## Development Roadmap
### Phase 1 — Infrastructure Modeling
 - Asset registry
 - Dependency modeling
 - Database schema design
### Phase 2 — Graph Intelligence
 - Centrality analysis
 - Traversal APIs
 - Bottleneck detection
### Phase 3 — Failure Simulation
 - Cascading propagation
 - Time-step simulation
 - Redundancy handling
### Phase 4 — Risk Scoring
 - Infrastructure fragility metrics
 - PSA-inspired scoring models
 - Resilience indicators
### Phase 5 — Scenario Engine
 - Multi-scenario comparison
 - What-if analysis
 - Stress testing workflows
### Phase 6 — Visualization & Analytics
 - Interactive dashboards
 - Graph visualization
 - Risk heatmaps

## Safety & Scope Note

This project is intended for educational, research, and engineering simulation purposes only.

The platform does not contain:

 - real nuclear facility data
 - classified infrastructure information
 - operational reactor control logic
 - sensitive infrastructure configurations

All infrastructure models are synthetic, abstracted, or generalized representations designed for systems engineering exploration.

## Why This Project Exists

Modern infrastructure systems are deeply interconnected.

Small failures in one subsystem can create disproportionate downstream consequences through hidden dependencies and cascading effects.

NuclearGridRisk explores how graph analytics, backend engineering, and simulation architecture can help model and better understand systemic infrastructure fragility.

## Future Directions

Potential future areas include:

 - Digital twin modeling
 - Infrastructure resilience scoring
 - AI-assisted anomaly simulation
 - Real-time event ingestion
 - Distributed simulation engines
 - Advanced graph databases
 - Geospatial infrastructure mapping

## License

MIT License