from collections import deque
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

        impacted_ids: set[str] = set()
        queue = deque([failed_asset_id_str])

        while queue:
            current_asset_id = queue.popleft()

            for _, downstream_asset_id, edge_data in graph.out_edges(current_asset_id, data=True):
                strength = edge_data.get("strength", 0.0)

                if strength < propagation_threshold:
                    continue

                if downstream_asset_id in impacted_ids:
                    continue

                impacted_ids.add(downstream_asset_id)
                queue.append(downstream_asset_id)

        impacted_assets = []

        for asset_id in impacted_ids:
            node_data = graph.nodes[asset_id]

            impacted_assets.append(
                {
                    "asset_id": asset_id,
                    "name": node_data["name"],
                    "asset_type": node_data["asset_type"],
                    "criticality": node_data["criticality"],
                }
            )

        return impacted_assets