from __future__ import annotations

from typing import Iterable

import networkx as nx
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.dependency import Dependency


class InfrastructureGraphBuilder:
    """Builds a directed infrastructure graph from database assets and dependencies."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def build(self) -> nx.DiGraph:
        assets = self._load_assets()
        dependencies = self._load_dependencies()

        return self._build_graph(assets=assets, dependencies=dependencies)

    def _load_assets(self) -> list[Asset]:
        return self.db.query(Asset).all()

    def _load_dependencies(self) -> list[Dependency]:
        return self.db.query(Dependency).all()

    def _build_graph(
        self,
        assets: Iterable[Asset],
        dependencies: Iterable[Dependency],
    ) -> nx.DiGraph:
        graph = nx.DiGraph()

        for asset in assets:
            graph.add_node(
                str(asset.id),
                id=str(asset.id),
                name=asset.name,
                asset_type=asset.asset_type,
                criticality=asset.criticality,
                status=asset.status,
            )

        for dependency in dependencies:
            graph.add_edge(
                str(dependency.source_asset_id),
                str(dependency.target_asset_id),
                id=str(dependency.id),
                dependency_type=dependency.dependency_type,
                strength=dependency.strength,
                failure_delay_minutes=dependency.failure_delay_minutes,
            )

        return graph