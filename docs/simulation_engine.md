# Simulation Engine
## Overview

NuclearGridRisk includes a graph-based deterministic infrastructure failure propagation engine designed to simulate cascading disruptions across interconnected infrastructure assets.

The simulation engine models:
 - directed infrastructure dependencies
 - threshold-based propagation
 - delayed cascading failures
 - redundancy-aware resilience behavior
 - temporal event propagation
 - failure-state transitions
 - infrastructure risk scoring

## Core Concepts
### Assets

Infrastructure components represented as graph nodes.

Examples:
 - external power grid
 - substations
 - cooling systems
 - monitoring systems
 - emergency generators

Each asset includes:
 - criticality score
 - asset type
 - operational metadata

### Dependencies

Directed relationships between assets.

Example:
 - External Grid → Substation → Cooling System

Dependency edges include:
| Field                   | Purpose                     |
| ----------------------- | --------------------------- |
| `strength`              | propagation severity        |
| `failure_delay_minutes` | temporal propagation delay  |
| `dependency_type`       | power/network/control/etc   |
| `redundancy_group`      | redundant upstream grouping |

### Graph Architecture

The infrastructure network is represented using:
 - `networkx.DiGraph`

Node metadata:
 - `id`
 - `name`
 - `asset_type`
 - `criticality`
 - `status`

Edge metadata:
 - `dependency_type`
 - `strength`
 - `failure_delay_minutes`
 - `redundancy_group`

## Failure Propagation

### Threshold-Based Propagation

Failure only propagates when dependency strength exceeds the configured threshold.

Example:
 - strength >= 0.7 → propagate
 - strength < 0.7 → stop propagation

## Time-Step Simulation

The simulation engine processes cascading failures using a deterministic event queue.

### Example:
 - t=0: External Grid fails
 - t=10: Substation impacted
 - t=30: Cooling System impacted

Propagation delays are accumulated across dependency paths.

## Failure States

The engine currently supports:

| State      | Meaning                                          |
| ---------- | ------------------------------------------------ |
| `failed`   | direct or severe infrastructure failure          |
| `degraded` | partial operational degradation                  |
| `isolated` | disconnected from required upstream dependencies |

## Redundancy Logic

Assets may have multiple redundant upstream dependencies.

### Example:
```
Grid A ─┐
        ├── Cooling System
Grid B ─┘
```

If one upstream dependency fails while another remains operational within the same redundancy group, propagation is suppressed.

## Multi-Source Failure Simulation

The engine supports simultaneous initial failures.

### Example:
```
Grid A + Grid B fail simultaneously
```
This enables future support for:

 - common-mode failures
 - natural disaster scenarios
 - coordinated cyber attacks
 - regional grid collapse simulation

## Risk Scoring

Simulation output includes deterministic risk scoring.

Current scoring model:
```
risk_score = Σ(asset criticality × state weight)
```

Current state weights:
| State    | Weight |
| -------- | ------ |
| failed   | 1.0    |
| isolated | 0.8    |
| degraded | 0.4    |

Risk levels:
| Score     | Level  |
| --------- | ------ |
| 0.0 - 1.0 | low    |
| 1.1 - 2.5 | medium |
| 2.6+      | high   |

## Current Capabilities

Implemented:
 - graph-based infrastructure modeling
 - traversal analysis
 - deterministic cascading failure propagation
 - delayed propagation simulation
 - redundancy-aware resilience logic
 - failure-state transitions
 - simulation timeline generation
 - infrastructure risk scoring

## Planned Enhancements

Future roadmap:
 - probabilistic propagation
 - Monte Carlo scenario simulation
 - LOOP / LOSP / SBO scoring
 - recovery simulation
 - repair scheduling
 - common-mode failure modeling
 - safety margin decay
 - dynamic resilience scoring
 - visualization layer
 - digital twin dashboards