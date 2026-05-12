from uuid import UUID

import networkx as nx
from sqlalchemy.orm import Session

from app.graph.builder import InfrastructureGraphBuilder


class FailureImpactService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.graph_builder = InfrastructureGraphBuilder(db)

    def get_downstream_impact(self, failed_asset_id: UUID) -> list[dict]:
        graph = self.graph_builder.build()
        failed_asset_id_str = str(failed_asset_id)

        if failed_asset_id_str not in graph:
            return []

        impacted_ids = nx.descendants(graph, failed_asset_id_str)

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