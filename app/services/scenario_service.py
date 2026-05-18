from sqlalchemy.orm import Session

from app.models.scenario import Scenario
from app.schemas.scenario import ScenarioCreate


class ScenarioService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_scenario(self, scenario_data: ScenarioCreate) -> Scenario:
        scenario = Scenario(
            name=scenario_data.name,
            scenario_type=scenario_data.scenario_type,
            initial_failed_asset_ids=[
                str(asset_id)
                for asset_id in scenario_data.initial_failed_asset_ids
            ],
            assumptions=scenario_data.assumptions,
            propagation_threshold=scenario_data.propagation_threshold,
            max_time_minutes=scenario_data.max_time_minutes,
        )

        self.db.add(scenario)
        self.db.commit()
        self.db.refresh(scenario)

        return scenario

    def list_scenarios(self) -> list[Scenario]:
        return self.db.query(Scenario).all()