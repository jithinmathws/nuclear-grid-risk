from collections import deque
from heapq import heappop, heappush
from uuid import UUID

from sqlalchemy.orm import Session

from app.graph.builder import InfrastructureGraphBuilder


class FailureImpactService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.graph_builder = InfrastructureGraphBuilder(db)

    def get_downstream_impact(
        self,
        failed_asset_id: UUID,
        propagation_threshold: float = 0.7,
    ) -> list[dict]:
        graph = self.graph_builder.build()

        failed_asset_id_str = str(failed_asset_id)

        if failed_asset_id_str not in graph:
            return []

        impact_metadata: dict[str, dict] = {}
        queue = deque([failed_asset_id_str])

        while queue:
            current_asset_id = queue.popleft()

            for _, downstream_asset_id, edge_data in graph.out_edges(current_asset_id, data=True):
                strength = edge_data.get("strength", 0.0)

                if strength < propagation_threshold:
                    continue

                if downstream_asset_id in impact_metadata:
                    continue

                impact_metadata[downstream_asset_id] = {
                    "caused_by_asset_id": current_asset_id,
                    "dependency_type": edge_data.get("dependency_type"),
                    "propagation_strength": strength,
                }

                queue.append(downstream_asset_id)

        impacted_assets = []

        for asset_id, metadata in impact_metadata.items():
            node_data = graph.nodes[asset_id]

            impacted_assets.append(
                {
                    "asset_id": asset_id,
                    "name": node_data["name"],
                    "asset_type": node_data["asset_type"],
                    "criticality": node_data["criticality"],
                    "caused_by_asset_id": metadata["caused_by_asset_id"],
                    "dependency_type": metadata["dependency_type"],
                    "propagation_strength": metadata["propagation_strength"],
                }
            )

        return impacted_assets

    def simulate_time_step_failure(
        self,
        failed_asset_id: UUID,
        propagation_threshold: float = 0.7,
        max_time_minutes: int = 60,
    ) -> list[dict]:
        graph = self.graph_builder.build()

        failed_asset_id_str = str(failed_asset_id)

        if failed_asset_id_str not in graph:
            return []

        visited: set[str] = set()
        timeline: list[dict] = []
        event_queue: list[tuple[int, str, str | None, dict | None]] = []

        heappush(event_queue, (0, failed_asset_id_str, None, None))

        while event_queue:
            current_time, asset_id, caused_by_asset_id, edge_data = heappop(event_queue)

            if current_time > max_time_minutes:
                continue

            if asset_id in visited:
                continue

            visited.add(asset_id)

            node_data = graph.nodes[asset_id]

            timeline.append(
                {
                    "asset_id": asset_id,
                    "name": node_data["name"],
                    "asset_type": node_data["asset_type"],
                    "criticality": node_data["criticality"],
                    "state": "failed"
                    if caused_by_asset_id is None
                    else self._resolve_failure_state(edge_data.get("strength", 0.0)),
                    "time_minute": current_time,
                    "caused_by_asset_id": caused_by_asset_id,
                    "dependency_type": edge_data.get("dependency_type") if edge_data else None,
                    "propagation_strength": edge_data.get("strength") if edge_data else None,
                }
            )

            for _, downstream_asset_id, downstream_edge_data in graph.out_edges(asset_id, data=True):
                strength = downstream_edge_data.get("strength", 0.0)

                if strength < propagation_threshold:
                    continue

                delay = downstream_edge_data.get("failure_delay_minutes", 0) or 0
                impacted_time = current_time + delay

                heappush(
                    event_queue,
                    (
                        impacted_time,
                        downstream_asset_id,
                        asset_id,
                        downstream_edge_data,
                    ),
                )

        return sorted(timeline, key=lambda event: event["time_minute"])

    def _resolve_failure_state(self, strength: float) -> str:
        if strength >= 0.85:
            return "failed"

        return "degraded"