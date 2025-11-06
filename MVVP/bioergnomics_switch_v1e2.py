# === OBINexus Bio-Ergnomic Switch v1.2 ===
# UK-Centric Inference Bias (User: @okpalanx, UK-based)
# Fixed: US case was inferring UK due to global bias
# Now: true_region = ground truth, inference only for UNKNOWN

import random
from enum import Enum
from typing import Tuple

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
    NIL = "nil"

# Iota (default) mappings
IOTA = {
    Region.UK: {SwitchPosition.UP: LightState.ON, SwitchPosition.DOWN: LightState.OFF},
    Region.US: {SwitchPosition.UP: LightState.OFF, SwitchPosition.DOWN: LightState.ON}
}

def H(region: Region, pos: SwitchPosition) -> LightState:
    return IOTA.get(region, {}).get(pos, LightState.NIL)

# UK-biased inference (user in UK → 95.4% prior)
def infer_region_uk_bias() -> Region:
    return Region.UK if random.random() < 0.954 else Region.US

class BioSwitch:
    def __init__(self, true_region: Region = Region.UNKNOWN):
        self.true_region = true_region
        self.inferred_region = Region.UNKNOWN
        self.coherence = 0.0
        self.delegations = 0

    def interpret(self, position: SwitchPosition, infer: bool = True) -> Tuple[LightState, float]:
        # Only infer if true_region unknown
        if self.true_region == Region.UNKNOWN and infer and self.inferred_region == Region.UNKNOWN:
            self.inferred_region = infer_region_uk_bias()

        # Use inferred only if no truth
        region = self.inferred_region if self.inferred_region != Region.UNKNOWN else self.true_region
        result = H(region, position)

        # Coherence: only vs true_region
        if self.true_region != Region.UNKNOWN:
            expected = IOTA[self.true_region][position]
            self.coherence = 1.0 if result == expected else 0.0
            if self.coherence < 0.954:
                self.delegations += 1
                alt = Region.US if region == Region.UK else Region.UK
                result = H(alt, position)
                self.coherence = 1.0
        else:
            self.coherence = 0.954  # assumed under nil

        return result, self.coherence

# === UK-Centric Demo ===
if __name__ == "__main__":
    print("OBINexus Bio-Ergnomic Light Switch v1.2 [UK Bias]\n")
    
    scenarios = [
        (Region.UK, SwitchPosition.UP, "UK: up → ON"),
        (Region.US, SwitchPosition.DOWN, "US: down → ON"),
        (Region.UK, SwitchPosition.DOWN, "UK: down → OFF"),
        (Region.UNKNOWN, SwitchPosition.UP, "Nil context → UK bias")
    ]

    for true_region, pos, note in scenarios:
        switch = BioSwitch(true_region)
        state, coh = switch.interpret(pos)
        delegated = switch.delegations > 0
        inf = switch.inferred_region.value if switch.inferred_region != Region.UNKNOWN else "?"
        print(f"{note}")
        print(f"   Input: {pos.value:>4} | True: {true_region.value:>7} | Infer: {inf:>3} | Out: {state.value:>3} | Coh: {coh:>5.1%}")
        print(f"   Heal: {delegated}\n")
