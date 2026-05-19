from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.simulation_run import SimulationRun
from app.schemas.simulation_run_analytics import SimulationRunMetricsResponse
from app.schemas.high_risk_simulation_run import HighRiskSimulationRunResponse


class SimulationRunAnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_metrics(self) -> SimulationRunMetricsResponse:
        summary_stmt = select(
            func.count(SimulationRun.id),
            func.avg(SimulationRun.risk_score),
            func.max(SimulationRun.risk_score),
            func.avg(SimulationRun.max_cascade_depth),
        )

        total_runs, average_risk_score, highest_risk_score, average_cascade_depth = self.db.execute(summary_stmt).one()

        distribution_stmt = (
            select(
                SimulationRun.risk_level,
                func.count(SimulationRun.id),
            )
            .where(SimulationRun.risk_level.is_not(None))
            .group_by(SimulationRun.risk_level)
        )

        distribution_rows = self.db.execute(distribution_stmt).all()

        risk_level_distribution = {
            risk_level: count
            for risk_level, count in distribution_rows
        }

        most_common_risk_level = None
        if risk_level_distribution:
            most_common_risk_level = max(
                risk_level_distribution,
                key=risk_level_distribution.get,
            )

        return SimulationRunMetricsResponse(
            total_runs=total_runs,
            average_risk_score=round(float(average_risk_score), 2) if average_risk_score is not None else None,
            highest_risk_score=float(highest_risk_score) if highest_risk_score is not None else None,
            most_common_risk_level=most_common_risk_level,
            average_cascade_depth=round(float(average_cascade_depth), 2) if average_cascade_depth is not None else None,
            risk_level_distribution=risk_level_distribution,
        )

    def get_high_risk_runs(
        self,
        min_score: float = 70.0,
        limit: int = 10,
    ) -> list[HighRiskSimulationRunResponse]:
        stmt = (
            select(SimulationRun)
            .where(SimulationRun.risk_score >= min_score)
            .order_by(
                SimulationRun.risk_score.desc(),
                SimulationRun.created_at.desc(),
            )
            .limit(limit)
        )

        runs = self.db.execute(stmt).scalars().all()

        return [
            HighRiskSimulationRunResponse.model_validate(run)
            for run in runs
        ]