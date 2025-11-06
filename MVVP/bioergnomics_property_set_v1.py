# bioergnomics_property_set_v1.py
# OBINexus: Property-Set Delegation (No Vectors)
# Pure state + context + healing via X/O nodes
# 95.4% coherence → solve, else delegate

from enum import Enum
from typing import Dict, Any, Tuple, Callable
import random

class Node(Enum):
    X = "X"
    O = "O"

class Property:
    """Open, global, delegatable trait"""
    def __init__(self, name: str, value: Any, owner: Node):
        self.name = name
        self.value = value
        self.owner = owner
        self.accessed_by = set()

    def read(self, reader: Node) -> Any:
        self.accessed_by.add(reader)
        return self.value

    def write(self, writer: Node, new_value: Any):
        if self.owner == writer or self.owner in self.accessed_by:
            self.value = new_value
            self.owner = writer  # ownership transfers on write
            return True
        return False

class PropertySet:
    """Global, open property container"""
    def __init__(self):
        self.props: Dict[str, Property] = {}
        self.coherence = 1.0
        self.delegations = 0

    def add(self, prop: Property):
        self.props[prop.name] = prop

    def get(self, name: str, reader: Node) -> Any:
        if name in self.props:
            return self.props[name].read(reader)
        return None

    def set(self, name: str, value: Any, writer: Node) -> bool:
        if name in self.props:
            success = self.props[name].write(writer, value)
            if not success:
                self.delegations += 1
                # Healing: force delegate to other node
                alt = Node.O if writer == Node.X else Node.X
                return self.props[name].write(alt, value)
            return success
        return False

    def check_coherence(self, expected: Dict[str, Any]) -> float:
        matched = sum(1 for k, v in expected.items() if self.get(k, Node.X) == v)
        self.coherence = matched / len(expected) if expected else 0.0
        return self.coherence

# === X/O Symbiotic Nodes ===
class SymbioticNode:
    def __init__(self, id: Node, pset: PropertySet):
        self.id = id
        self.pset = pset

    def task(self, goal: Dict[str, Any]) -> Tuple[bool, float]:
        # Try to solve locally
        for k, v in goal.items():
            current = self.pset.get(k, self.id)
            if current != v:
                success = self.pset.set(k, v, self.id)
                if not success:
                    return False, self.pset.coherence

        coh = self.pset.check_coherence(goal)
        return coh >= 0.954, coh

# === Demo: Light Switch via Property Delegation (No Vectors) ===
if __name__ == "__main__":
    print("OBINexus Property-Set Delegation v1.0 [No Vectors]\n")

    pset = PropertySet()
    pset.add(Property("switch_position", "up", Node.X))
    pset.add(Property("light_state", "off", Node.O))
    pset.add(Property("region", "UK", Node.X))

    node_X = SymbioticNode(Node.X, pset)
    node_O = SymbioticNode(Node.O, pset)

    scenarios = [
        ({"region": "UK", "switch_position": "up"}, "light_state", "on", "UK: up → on"),
        ({"region": "US", "switch_position": "down"}, "light_state", "on", "US: down → on"),
        ({"region": "UK", "switch_position": "down"}, "light_state", "off", "UK: down → off"),
    ]

    for goal_state, target_prop, expected_val, note in scenarios:
        print(f"{note}")

        # Node X tries first
        success, coh = node_X.task(goal_state)
        if not success and coh < 0.954:
            print(f"   X failed ({coh:.1%}) → delegate to O")
            success, coh = node_O.task(goal_state)

        final = pset.get(target_prop, Node.X)
        delegated = pset.delegations > 0
        print(f"   Goal: {goal_state}")
        print(f"   Final {target_prop}: {final} | Expected: {expected_val} | Coh: {coh:.1%}")
        print(f"   Delegated: {delegated}\n")
        pset.delegations = 0  # reset
