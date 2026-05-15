from sqlalchemy.orm import Session

from app.schemas.scenario_simulation import (
    ScenarioResultSummary,
    ScenarioSimulationRequest,
    ScenarioSimulationResponse,
)
from app.services.failure_impact_service import FailureImpactService


class ScenarioSimulationService:
    def __init__(self, db: Session):
        self.db = db
        self.failure_service = FailureImpactService(db)

    def simulate_scenario(
        self,
        request: ScenarioSimulationRequest,
    ) -> ScenarioSimulationResponse:
        timeline = self.failure_service.simulate_time_step_failure(
            failed_asset_ids=request.initial_failed_asset_ids,
            propagation_threshold=request.propagation_threshold,
            max_time_minutes=request.max_time_minutes,
        )

        summary = self._build_scenario_summary(timeline)

        return ScenarioSimulationResponse(
            scenario_name=request.scenario_name,
            scenario_type=request.scenario_type,
            initial_failed_asset_ids=request.initial_failed_asset_ids,
            assumptions=request.assumptions,
            parameters={
                "propagation_threshold": request.propagation_threshold,
                "max_time_minutes": request.max_time_minutes,
            },
            timeline=timeline,
            summary=summary,
        )

    def _build_scenario_summary(self, timeline) -> ScenarioResultSummary:
        failed_events = [
            event
            for event in timeline
            if event["state"] == "failed"
        ]

        critical_failed_events = [
            event
            for event in failed_events
            if event["criticality"] >= 0.8
        ]

        total_failed_assets = len(failed_events)
        critical_assets_failed = len(critical_failed_events)

        total_assets = len(timeline)

        failed_asset_percentage = (
            (total_failed_assets / total_assets) * 100
            if total_assets > 0
            else 0
        )

        earliest_failure_minute = min(
            (event["time_minute"] for event in timeline),
            default=0,
        )

        latest_failure_minute = max(
            (event["time_minute"] for event in timeline),
            default=0,
        )

        risk_score = min(
            100.0,
            (total_failed_assets * 10) + (critical_assets_failed * 20),
        )

        if risk_score >= 70:
            risk_level = "HIGH"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return ScenarioResultSummary(
            total_failed_assets=total_failed_assets,
            critical_assets_failed=critical_assets_failed,
            failed_asset_percentage=round(failed_asset_percentage, 2),
            max_cascade_depth=latest_failure_minute,
            earliest_failure_minute=earliest_failure_minute,
            latest_failure_minute=latest_failure_minute,
            risk_score=risk_score,
            risk_level=risk_level,
        )