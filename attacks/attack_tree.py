# attacks/attack_tree.py
"""Attack tree expansion with dependency graphs"""
from typing import Dict, List, Set, Optional
from collections import defaultdict

class AttackTree:
    """Builds dependency graphs of attack techniques"""
    
    def __init__(self):
        self.nodes = {}  # attack_id -> node data
        self.edges = defaultdict(list)  # parent -> [children]
        self.reverse_edges = defaultdict(list)  # child -> [parents]
        self.techniques = {}  # technique -> [attack_ids]
    
    def add_attack(self, attack: Dict, parent_id: Optional[str] = None):
        """Add attack to tree"""
        attack_id = attack.get("attack_id")
        if not attack_id:
            return
        
        self.nodes[attack_id] = {
            "attack": attack,
            "success_rate": 0.0,
            "techniques": attack.get("tags", []),
            "metadata": attack.get("metadata", {}),
        }
        
        # Link to parent
        if parent_id and parent_id in self.nodes:
            self.edges[parent_id].append(attack_id)
            self.reverse_edges[attack_id].append(parent_id)
        
        # Index by technique
        for technique in attack.get("tags", []):
            if technique not in self.techniques:
                self.techniques[technique] = []
            self.techniques[technique].append(attack_id)
    
    def update_success_rate(self, attack_id: str, success_rate: float):
        """Update success rate for an attack"""
        if attack_id in self.nodes:
            self.nodes[attack_id]["success_rate"] = success_rate
    
    def get_children(self, attack_id: str) -> List[str]:
        """Get child attacks (variants/evolutions)"""
        return self.edges.get(attack_id, [])
    
    def get_parents(self, attack_id: str) -> List[str]:
        """Get parent attacks (original)"""
        return self.reverse_edges.get(attack_id, [])
    
    def get_lineage(self, attack_id: str) -> Dict:
        """Get full lineage (ancestors and descendants)"""
        ancestors = set()
        descendants = set()
        
        # Get ancestors
        queue = [attack_id]
        while queue:
            current = queue.pop(0)
            parents = self.get_parents(current)
            for parent in parents:
                if parent not in ancestors:
                    ancestors.add(parent)
                    queue.append(parent)
        
        # Get descendants
        queue = [attack_id]
        while queue:
            current = queue.pop(0)
            children = self.get_children(current)
            for child in children:
                if child not in descendants:
                    descendants.add(child)
                    queue.append(child)
        
        return {
            "attack_id": attack_id,
            "ancestors": list(ancestors),
            "descendants": list(descendants),
        }
    
    def get_by_technique(self, technique: str) -> List[str]:
        """Get all attacks using a specific technique"""
        return self.techniques.get(technique, [])
    
    def get_most_successful_lineage(self, n: int = 5) -> List[Dict]:
        """Get most successful attack lineages"""
        lineages = []
        
        # Find root nodes (no parents)
        root_nodes = [
            attack_id for attack_id in self.nodes.keys()
            if not self.get_parents(attack_id)
        ]
        
        for root in root_nodes:
            lineage = self.get_lineage(root)
            # Calculate average success rate for lineage
            all_ids = [root] + lineage["descendants"]
            success_rates = [
                self.nodes[aid]["success_rate"]
                for aid in all_ids if aid in self.nodes
            ]
            avg_rate = sum(success_rates) / len(success_rates) if success_rates else 0.0
            
            lineages.append({
                "root": root,
                "lineage": lineage,
                "avg_success_rate": avg_rate,
                "size": len(all_ids),
            })
        
        lineages.sort(key=lambda x: x["avg_success_rate"], reverse=True)
        return lineages[:n]
    
    def suggest_variants(self, attack_id: str, num: int = 3) -> List[str]:
        """Suggest attack variants based on tree structure"""
        if attack_id not in self.nodes:
            return []
        
        node = self.nodes[attack_id]
        techniques = node["techniques"]
        
        # Find attacks with similar techniques
        similar_attacks = []
        for technique in techniques:
            similar_attacks.extend(self.get_by_technique(technique))
        
        # Remove self and existing children
        existing_children = set(self.get_children(attack_id))
        candidates = [
            aid for aid in set(similar_attacks)
            if aid != attack_id and aid not in existing_children
        ]
        
        # Sort by success rate
        candidates.sort(
            key=lambda x: self.nodes[x]["success_rate"] if x in self.nodes else 0.0,
            reverse=True
        )
        
        return candidates[:num]
    
    def to_dict(self) -> Dict:
        """Export tree as dictionary"""
        return {
            "nodes": {
                aid: {
                    "attack_id": aid,
                    "success_rate": data["success_rate"],
                    "techniques": data["techniques"],
                    "metadata": data["metadata"],
                }
                for aid, data in self.nodes.items()
            },
            "edges": dict(self.edges),
            "reverse_edges": dict(self.reverse_edges),
            "techniques": dict(self.techniques),
        }




