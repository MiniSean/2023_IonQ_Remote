from dataclasses import dataclass
from random import randint, sample, seed
from typing import List, Union, Tuple
from enum import Enum

class GateType(Enum):
    x = 'x'
    h = 'h'
    i = 'i'

@dataclass(frozen=True)
class NConditionalGate:
    """
    Data class describing a requested n-conditional gate.
    Where control and target indices correspond to qubit indices in a circuit.
    Where gate type should be 'X' or 'H' (hadamard).
    """
    control_idx: List[int]  # Qubit circuit index
    control_state: List[int]  # (Qubit) States are either 0 or 1
    target_idx: int  # Qubit circuit index
    gate_type: GateType
    
    def join(self, other: 'NConditionalGate') -> List['NConditionalGate']:
        if self.control_idx == other.control_idx and self.control_state == other.control_state and self.target_idx == other.target_idx and self.gate_type == other.gate_type:
            return []
        return [self, other]


def to_bit(i: int) -> str: return format(i, '#011b')
def to_int(b: str) -> int: return int(b, 2)
def get_state(b: str, idx: int) -> int: return int(b[2 + idx])
def get_states(b: str, idxs: List[int]) -> List[int]: return [get_state(b, idx) for idx in idxs] 

@dataclass(frozen=True)
class SplitResult:
    idx: int
    zero_based: List[str]
    one_based: List[str]
    
    def get_required_gates(self) -> List[NConditionalGate]:
        # Guard clause, if 1-based is empty, return identity.
        if len(self.one_based) == 0:
            return [
                NConditionalGate(
                    control_idx=[],
                    control_state=[],
                    target_idx=self.idx,
                    gate_type=GateType.i,
                )
            ]
        
        control_idx: List[int] = list(range(self.idx))
        
        # Guard clause, if 0-based is empty, return conditional X gate (based on all prior qubits)
        if len(self.zero_based) == 0:
            return [
                NConditionalGate(
                    control_idx=control_idx,
                    control_state=get_states(s, control_idx),
                    target_idx=self.idx,
                    gate_type=GateType.x,
                )
                for s in self.one_based
            ]
        
        # Else, (both zero- and one-based arrays are not empty) place conditional hadamard
        return [
            NConditionalGate(
                control_idx=control_idx,
                control_state=get_states(s, control_idx),
                target_idx=self.idx,
                gate_type=GateType.h,
            )
            for s in self.zero_based + self.one_based
        ]

# Organaze based on first index
def split_bitstring(s_array: List[str], idx: int) -> SplitResult:
    return SplitResult(
        idx=idx,
        zero_based=[s for s in s_array if get_state(s, idx) == 0],
        one_based=[s for s in s_array if get_state(s, idx) == 1],
    )

def iterate_bitstring(bitstring: List[str], idx: int) -> List[SplitResult]:
    end_result: List[SplitResult] = []
    if len(bitstring) == 0 or idx >= len(bitstring[0]) - 2:
        return end_result
    
    split_result: SplitResult = split_bitstring(bitstring, idx)
    
    end_result.append(split_result)
    end_result.extend(iterate_bitstring(split_result.one_based, idx + 1))
    end_result.extend(iterate_bitstring(split_result.zero_based, idx + 1))
    
    return end_result


all_gates: List[NConditionalGate] = []

for split_result in iterate_bitstring(index_list, 0):
    all_gates.extend(split_result.get_required_gates())
    
# Fix duplicate gates
new_all_gates: List[NConditionalGate] = []
for gate in all_gates:
    # Guard clause first gate appended
    if len(new_all_gates) == 0:
        new_all_gates.append(gate)
        continue
        
    last_gate = new_all_gates.pop(-1)
    new_all_gates.extend(last_gate.join(gate))


print(len(new_all_gates), len(all_gates))
# for g in new_all_gates:
#     print(g)