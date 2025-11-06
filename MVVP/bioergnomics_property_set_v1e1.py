# bioergnomics_property_set_v1e1.py
# OBINexus: Property-Set Delegation v1.1 [UK Bias + Healing]
# Fixed: light_state not updated — now uses region to compute output
# No vectors. Pure state + context + X/O symbiosis

from enum import Enum
from typing import Dict, Any, Tuple
import random

class Node(Enum):
    X = "X"
    O = "O"

class Property:
    def __init__(self, name: str, value: Any, owner: Node):
        self.name = name
        self.value = value
        self.owner = owner
        self.accessed_by = set()

    def read(self, reader: Node) -> Any:
        self.accessed_by.add(reader)
        return self.value

    def write(self, writer: Node, new_value: Any) -> bool:
        if self.owner == writer or self.owner in self.accessed_by:
            self.value = new_value
            self.owner = writer
            return True
        return False

class PropertySet:
    def __init__(self):
        self.props: Dict[str, Property] = {}
        self.delegations = 0

    def add(self, prop: Property):
        self.props[prop.name] = prop

    def get(self, name: str, reader: Node) -> Any:
        if name in self.props:
            return self.props[name].read(reader)
        return None

    def set(self, name: str, value: Any, writer: Node) -> bool:
        if name in self.props:
            if not self.props[name].write(writer, value):
                self.delegations += 1
                alt = Node.O if writer == Node.X else Node.X
                return self.props[name].write(alt, value)
            return True
        return False

    def check_coherence(self, expected: Dict[str, Any]) -> float:
        matched = sum(1 for k, v in expected.items() if self.get(k, Node.X) == v)
        return matched / len(expected) if expected else 0.0

# === H-Function: region + switch → light_state ===
def compute_light_state(region: str, switch_pos: str) -> str:
    if region == "UK":
        return "on" if switch_pos == "up" else "off"
    elif region == "US":
        return "on" if switch_pos == "down" else "off"
    return "nil"

class SymbioticNode:
    def __init__(self, id: Node, pset: PropertySet):
        self.id = id
        self.pset = pset

    def task(self, goal: Dict[str, Any]) -> Tuple[bool, float]:
        # Update input properties
        for k, v in goal.items():
            self.pset.set(k, v, self.id)

        # Compute derived output
        region = self.pset.get("region", self.id)
        switch_pos = self.pset.get("switch_position", self.id)
        if region and switch_pos:
            target_state = compute_light_state(region, switch_pos)
            self.pset.set("light_state", target_state, self.id)

        # Coherence check
        expected = {"light_state": compute_light_state(goal.get("region", ""), goal.get("switch_position", ""))}
        coh = self.pset.check_coherence(expected)
        return coh >= 0.954, coh

# === Demo ===
if __name__ == "__main__":
    print("OBINexus Property-Set Delegation v1.1 [UK Bias + Healing]\n")

    pset = PropertySet()
    pset.add(Property("switch_position", "up", Node.X))
    pset.add(Property("light_state", "off", Node.X))
    pset.add(Property("region", "UK", Node.X))

    node_X = SymbioticNode(Node.X, pset)
    node_O = SymbioticNode(Node.O, pset)

    scenarios = [
        ({"region": "UK", "switch_position": "up"}, "on", "UK: up → on"),
        ({"region": "US", "switch_position": "down"}, "on", "US: down → on"),
        ({"region": "UK", "switch_position": "down"}, "off", "UK: down → off"),
    ]

    for goal_state, expected_val, note in scenarios:
        print(f"{note}")
        success, coh = node_X.task(goal_state)
        if not success and coh < 0.954:
            print(f"   X failed ({coh:.1%}) → delegate to O")
            success, coh = node_O.task(goal_state)

        final = pset.get("light_state", Node.X)
        delegated = pset.delegations > 0
        print(f"   Goal: {goal_state}")
        print(f"   Final light_state: {final} | Expected: {expected_val} | Coh: {coh:.1%}")
        print(f"   Delegated: {delegated}\n")
        pset.delegations = 0  # reset
