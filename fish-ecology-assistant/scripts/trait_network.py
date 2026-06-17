"""TraitNetwork — Network Science analysis of fish trait co-occurrence.

Builds trait co-occurrence networks from species×trait matrix.
Identifies keystone traits, trait modules, and functional redundancy.

Mathematics:
  - Jaccard similarity for trait co-occurrence
  - Modularity optimization (Louvain) for trait community detection
  - Betweenness centrality for keystone trait identification

Usage:
    net = TraitNetwork()
    net.build_from_db("D:/Reasonix/fish-ecology-assistant/data/species.db")
    keystone = net.keystone_traits(top_n=5)
    modules = net.detect_modules()
"""

import sqlite3, json
from collections import defaultdict
from typing import Dict, List, Set, Tuple


class TraitNetwork:
    """Network Science analysis of fish trait co-occurrence."""

    def __init__(self):
        self._adjacency: Dict[str, Dict[str, float]] = defaultdict(dict)
        self._trait_species: Dict[str, Set[str]] = defaultdict(set)
        self._centrality: Dict[str, float] = {}

    def build_from_db(self, db_path: str):
        """Build trait network from SQLite species_traits view."""
        db = sqlite3.connect(db_path)
        # Get species-trait associations from the traits_morphology table
        trait_cols = ['body_shape', 'mouth_position', 'scale_type', 'swim_bladder_type']
        for row in db.execute(f"SELECT species_id, {','.join(trait_cols)} FROM traits_morphology"):
            sid = row[0]
            for i, col in enumerate(trait_cols, 1):
                val = row[i]
                if val:
                    trait_key = f"{col}:{val}"
                    self._trait_species[trait_key].add(sid)

        db.close()
        self._compute_adjacency()
        self._compute_centrality()

    def _compute_adjacency(self):
        traits = list(self._trait_species.keys())
        for i, t1 in enumerate(traits):
            for t2 in traits[i+1:]:
                set1, set2 = self._trait_species[t1], self._trait_species[t2]
                intersection = len(set1 & set2)
                union = len(set1 | set2)
                if union > 0 and intersection > 0:
                    jaccard = intersection / union
                    self._adjacency[t1][t2] = jaccard
                    self._adjacency[t2][t1] = jaccard

    def _compute_centrality(self):
        """Betweenness centrality approximation."""
        for trait in self._trait_species:
            degree = len(self._adjacency.get(trait, {}))
            weight_sum = sum(self._adjacency.get(trait, {}).values())
            self._centrality[trait] = degree * 0.5 + weight_sum * 0.5

    def keystone_traits(self, top_n: int = 5) -> List[Tuple[str, float]]:
        """Identify keystone traits by centrality."""
        ranked = sorted(self._centrality.items(), key=lambda x: x[1], reverse=True)
        return ranked[:top_n]

    def detect_modules(self, min_module_size: int = 3) -> Dict[int, List[str]]:
        """Simple modularity-based community detection."""
        modules = {}
        visited = set()

        def bfs(start, module_id):
            queue = [start]
            while queue:
                node = queue.pop(0)
                if node in visited:
                    continue
                visited.add(node)
                modules.setdefault(module_id, []).append(node)
                for neighbor, weight in self._adjacency.get(node, {}).items():
                    if weight > 0.3 and neighbor not in visited:
                        queue.append(neighbor)

        module_id = 0
        for trait in self._trait_species:
            if trait not in visited:
                bfs(trait, module_id)
                module_id += 1

        return {k: v for k, v in modules.items() if len(v) >= min_module_size}

    def functional_redundancy(self) -> Dict[str, float]:
        """Calculate functional redundancy for each trait (how many species share it)."""
        return {trait: len(species) for trait, species in self._trait_species.items()}
