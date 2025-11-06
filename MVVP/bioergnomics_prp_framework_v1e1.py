# bioergnomics_prp_framework_v1e1.py
# OBINexus: PRP Framework v1.1 [Fixed + Coherent]
# UK-first, iota/nil, 95.4% threshold, state reset

from enum import Enum
from typing import Dict, Any, List, Tuple, Callable
import random

class Node(Enum):
    X = "X"
    O = "O"

class IotaState(Enum):
    UK = "UK"
    US = "US"
    NIL = "nil"

# === Property System ===
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
        self.iota = IotaState.UK

    def add(self, prop: Property):
        self.props[prop.name] = prop

    def get(self, name: str, reader: Node) -> Any:
        return self.props[name].read(reader) if name in self.props else None

    def set(self, name: str, value: Any, writer: Node) -> bool:
        if name in self.props:
            if not self.props[name].write(writer, value):
                self.delegations += 1
                alt = Node.O if writer == Node.X else Node.X
                return self.props[name].write(alt, value)
            return True
        return False

    def infer_iota(self) -> str:
        if self.iota == IotaState.NIL:
            self.iota = IotaState.UK if random.random() < 0.954 else IotaState.US
        return self.iota.value

    def reset(self):
        self.set("switch_position", "up", Node.X)
        self.set("region", "nil", Node.X)
        self.iota = IotaState.NIL
        self.delegations = 0

# === H-Function ===
def H(region: str, switch_pos: str) -> str:
    if region == "UK": return "on" if switch_pos == "up" else "off"
    if region == "US": return "on" if switch_pos == "down" else "off"
    return "nil"

# === PRP Resolver ===
class PRPFramework:
    COHERENCE_THRESHOLD = 0.954

    def __init__(self, pset: PropertySet):
        self.pset = pset
        self.resolvers: Dict[str, Callable] = {
            "flip": self._flip_switch,
            "rotate": self._rotate_context,
            "heal": self._heal_state,
        }

    def resolve(self, actions: List[Tuple[str, str]], goal: Dict[str, str]) -> Tuple[float, bool]:
        # Apply actions
        for verb, noun in actions:
            if verb in self.resolvers:
                self.resolvers[verb](noun)

        # Compute output
        region = self.pset.get("region", Node.X)
        if not region or region == "nil":
            region = self.pset.infer_iota()
        switch_pos = self.pset.get("switch_position", Node.X) or "up"
        light_state = H(region, switch_pos)
        self.pset.set("light_state", light_state, Node.X)

        # Coherence
        expected = goal.get("light_state")
        coh = 1.0 if light_state == expected else 0.0
        solved = coh >= self.COHERENCE_THRESHOLD
        return coh, solved

    def _flip_switch(self, noun: str):
        if noun == "switch":
            cur = self.pset.get("switch_position", Node.X)
            new = "down" if cur == "up" else "up"
            self.pset.set("switch_position", new, Node.X)

    def _rotate_context(self, noun: str):
        if noun == "context":
            cur = self.pset.get("region", Node.X)
            new = "US" if cur == "UK" else "UK"
            self.pset.set("region", new, Node.X)

    def _heal_state(self, noun: str):
        if noun == "state":
            self.pset.delegations += 1

# === Demo ===
if __name__ == "__main__":
    print("OBINexus PRP Framework v1.1 [95.4% Coherence]\n")

    pset = PropertySet()
    pset.add(Property("switch_position", "up", Node.X))
    pset.add(Property("light_state", "off", Node.X))
    pset.add(Property("region", "nil", Node.X))

    prp = PRPFramework(pset)

    scenarios = [
        ([("flip", "switch")], {"light_state": "off"}, "UK: flip → off"),
        ([("rotate", "context"), ("flip", "switch")], {"light_state": "on"}, "Rotate → US → flip → on"),
        ([], {"light_state": "on"}, "Nil context → UK bias → on"),
        ([("heal", "state")], {"light_state": "on"}, "Heal → delegate"),
    ]

    for actions, goal, note in scenarios:
        print(f"{note}")
        coh, solved = prp.resolve(actions, goal)
        delegated = pset.delegations > 0
        final = pset.get("light_state", Node.X)
        print(f"   Actions: {actions}")
        print(f"   Final: {final} | Goal: {goal['light_state']} | Coh: {coh:.1%} | Solved: {solved}")
        print(f"   Delegated: {delegated}\n")
        pset.reset()  # Reset for next
