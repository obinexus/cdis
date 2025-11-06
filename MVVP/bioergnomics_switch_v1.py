# OBINexus Bio-Ergnomic Switch Interpreter
# Directed Symbiosis via Context + Iota + Nil States
# Coherence ≥ 95.4% → Solve, else delegate

from enum import Enum
from typing import Callable, Tuple
import random

class Region(Enum):
    UK = "UK"
    US = "US"
    UNKNOWN = "UNKNOWN"

class SwitchPosition(Enum):
    UP = "up"
    DOWN = "down"

class LightState(Enum):
    ON = "on"
    OFF = "off"
    NIL = "nil"  # no context, no memory

# Iota (default) states per region
IOTA = {
    Region.UK: {SwitchPosition.UP: LightState.ON, SwitchPosition.DOWN: LightState.OFF},
    Region.US: {SwitchPosition.UP: LightState.OFF, SwitchPosition.DOWN: LightState.ON}
}

# Heterogeneous Mapping Function H(context, input) → output
def H(region: Region, position: SwitchPosition) -> LightState:
    if region in IOTA:
        return IOTA[region][position]
    return LightState.NIL

# Bayesian Context Inference (95.4% coherence proxy)
def infer_region(prob_uk: float = 0.6) -> Region:
    return Region.UK if random.random() < prob_uk else Region.US

# Master Interpreter with Healing & Delegation
class BioSwitch:
    def __init__(self, true_region: Region = Region.UNKNOWN):
        self.true_region = true_region
        self.inferred_region = Region.UNKNOWN
        self.coherence = 0.0
        self.delegations = 0

    def interpret(self, position: SwitchPosition, infer: bool = True) -> Tuple[LightState, float]:
        # Step 1: Infer context if unknown
        if self.inferred_region == Region.UNKNOWN and infer:
            self.inferred_region = infer_region(prob_uk=0.954)  # 95.4% UK bias possible

        region = self.inferred_region if self.inferred_region != Region.UNKNOWN else self.true_region

        # Step 2: Apply H-function
        result = H(region, position)

        # Step 3: Coherence check vs truth
        if self.true_region != Region.UNKNOWN:
            expected = IOTA[self.true_region][position]
            self.coherence = 1.0 if result == expected else 0.0
            if self.coherence < 0.954:
                self.delegations += 1
                # Healing: fallback to opposite assumption
                alt_region = Region.US if region == Region.UK else Region.UK
                result = H(alt_region, position)
                self.coherence = 1.0  # now healed
        else:
            self.coherence = 0.954  # assume coherence if no truth

        return result, self.coherence

# === DEMO ===
if __name__ == "__main__":
    print("OBINexus Bio-Ergnomic Light Switch v1.0\n")
    
    scenarios = [
        (Region.UK, SwitchPosition.UP, "Should be ON"),
        (Region.US, SwitchPosition.DOWN, "Should be ON"),
        (Region.UK, SwitchPosition.DOWN, "Should be OFF"),
        (Region.UNKNOWN, SwitchPosition.UP, "Nil context → infer")
    ]

    for true_region, pos, note in scenarios:
        switch = BioSwitch(true_region)
        state, coh = switch.interpret(pos)
        delegated = switch.delegations > 0
        print(f"{note}")
        print(f"   Input: {pos.value} | Inferred: {switch.inferred_region.value} | Output: {state.value} | Coherence: {coh:.1%}")
        print(f"   Delegated: {delegated}\n")
