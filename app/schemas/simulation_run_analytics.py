from pydantic import BaseModel


class SimulationRunMetricsResponse(BaseModel):
    total_runs: int
    average_risk_score: float | None
    highest_risk_score: float | None
    most_common_risk_level: str | None
    average_cascade_depth: float | None
    risk_level_distribution: dict[str, int]