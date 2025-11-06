# bioergnomics_verb_noun_dag_v1e1.py
# OBINexus: Verb-Noun DAG Interpreter v1.1 [Fixed + Coherent]
# UK-first, state-aware, proper H-function application

from enum import Enum
from typing import Dict, Any, List, Tuple
import random

class Node(Enum):
    X = "X"
    O = "O"

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

# === H-Function ===
def compute_light_state(region: str, switch_pos: str) -> str:
    if region == "UK":
        return "on" if switch_pos == "up" else "off"
    elif region == "US":
        return "on" if switch_pos == "down" else "off"
    return "nil"

# === Verb-Noun DAG ===
class VerbNounPair:
    def __init__(self, verb: str, noun: str):
        self.verb = verb
        self.noun = noun

    def __str__(self):
        return f"{self.verb}-{self.noun}"

class OpenInterpreter:
    def __init__(self, pset: PropertySet):
        self.pset = pset
        self.resolvers = {
            "flip": self._resolve_flip,
            "heal": self._resolve_heal,
            "rotate": self._resolve_rotate,
        }

    def interpret(self, pairs: List[VerbNounPair]) -> Tuple[str, float]:
        # Execute verbs in order
        for pair in pairs:
            if pair.verb in self.resolvers:
                self.resolvers[pair.verb](pair.noun)

        # Always recompute light_state via H
        region = self.pset.get("region", Node.X) or "UK"
        switch_pos = self.pset.get("switch_position", Node.X) or "up"
        light_state = compute_light_state(region, switch_pos)
        self.pset.set("light_state", light_state, Node.X)

        # Coherence: light on = 100%, off = 0%
        coh = 1.0 if light_state == "on" else 0.0
        return light_state, coh

    def _resolve_flip(self, noun: str):
        if noun == "switch":
            cur = self.pset.get("switch_position", Node.X)
            new = "down" if cur == "up" else "up"
            self.pset.set("switch_position", new, Node.X)

    def _resolve_heal(self, noun: str):
        if noun == "state":
            self.pset.delegations += 1

    def _resolve_rotate(self, noun: str):
        if noun == "context":
            cur = self.pset.get("region", Node.X)
            new = "US" if cur == "UK" else "UK"
            self.pset.set("region", new, Node.X)

# === Demo ===
if __name__ == "__main__":
    print("OBINexus Verb-Noun DAG Interpreter v1.1 [Coherent]\n")

    pset = PropertySet()
    pset.add(Property("switch_position", "up", Node.X))
    pset.add(Property("light_state", "off", Node.X))
    pset.add(Property("region", "UK", Node.X))

    interpreter = OpenInterpreter(pset)

    scenarios = [
        ([VerbNounPair("flip", "switch")], "UK: flip → off"),
        ([VerbNounPair("rotate", "context"), VerbNounPair("flip", "switch")], "Rotate to US → flip → on"),
        ([VerbNounPair("heal", "state")], "Heal → delegate"),
    ]

    for pairs, note in scenarios:
        print(f"{note}")
        state, coh = interpreter.interpret(pairs)
        delegated = pset.delegations > 0
        print(f"   Input: {[str(p) for p in pairs]}")
        print(f"   Final: {state} | Coh: {coh:.1%} | Delegated: {delegated}")
        print()
        pset.delegations = 0
        # Reset for next
        pset.set("switch_position", "up", Node.X)
        pset.set("region", "UK", Node.X)
