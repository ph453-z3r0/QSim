from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional
import math

from qiskit import QuantumCircuit
import cirq


@dataclass(frozen=True)
class GateDefinition:
    """Metadata and factory functions for a quantum gate."""

    name: str
    category: str
    description: str
    qubits: int
    qiskit_builder: Callable[[], QuantumCircuit]
    cirq_builder: Optional[Callable[[], cirq.Circuit]] = None


def _single_qubit_circuit(builder: Callable[[QuantumCircuit], None]) -> Callable[[], QuantumCircuit]:
    def factory() -> QuantumCircuit:
        circuit = QuantumCircuit(1, name="single_qubit")
        builder(circuit)
        circuit.barrier()
        circuit.measure_all(add_bits=False)
        return circuit

    return factory


def _two_qubit_circuit(builder: Callable[[QuantumCircuit], None]) -> Callable[[], QuantumCircuit]:
    def factory() -> QuantumCircuit:
        circuit = QuantumCircuit(2, name="two_qubit")
        builder(circuit)
        circuit.barrier()
        circuit.measure_all(add_bits=False)
        return circuit

    return factory


def _three_qubit_circuit(builder: Callable[[QuantumCircuit], None]) -> Callable[[], QuantumCircuit]:
    def factory() -> QuantumCircuit:
        circuit = QuantumCircuit(3, name="three_qubit")
        builder(circuit)
        circuit.barrier()
        circuit.measure_all(add_bits=False)
        return circuit

    return factory


def _cirq_single(gate: cirq.Gate) -> Callable[[], cirq.Circuit]:
    def factory() -> cirq.Circuit:
        qubit = cirq.LineQubit(0)
        return cirq.Circuit(gate.on(qubit), cirq.measure(qubit, key="m0"))

    return factory


def _cirq_two(gate: cirq.Gate) -> Callable[[], cirq.Circuit]:
    def factory() -> cirq.Circuit:
        q0, q1 = cirq.LineQubit.range(2)
        return cirq.Circuit(gate.on(q0, q1), cirq.measure(q0, q1, key="m"))

    return factory


def _cirq_three(gate: cirq.Gate) -> Callable[[], cirq.Circuit]:
    def factory() -> cirq.Circuit:
        q0, q1, q2 = cirq.LineQubit.range(3)
        return cirq.Circuit(gate.on(q0, q1, q2), cirq.measure(q0, q1, q2, key="m"))

    return factory


GATE_LIBRARY: Dict[str, GateDefinition] = {
    "I": GateDefinition(
        name="Identity",
        category="Pauli & Identity",
        description="Leaves the qubit state unchanged.",
        qubits=1,
        qiskit_builder=_single_qubit_circuit(lambda qc: qc.id(0)),
        cirq_builder=_cirq_single(cirq.I),
    ),
    "X": GateDefinition(
        name="Pauli-X",
        category="Pauli & Identity",
        description="Bit-flip gate analogous to classical NOT.",
        qubits=1,
        qiskit_builder=_single_qubit_circuit(lambda qc: qc.x(0)),
        cirq_builder=_cirq_single(cirq.X),
    ),
    "Y": GateDefinition(
        name="Pauli-Y",
        category="Pauli & Identity",
        description="Combined bit- and phase-flip gate.",
        qubits=1,
        qiskit_builder=_single_qubit_circuit(lambda qc: qc.y(0)),
        cirq_builder=_cirq_single(cirq.Y),
    ),
    "Z": GateDefinition(
        name="Pauli-Z",
        category="Pauli & Identity",
        description="Phase-flip gate.",
        qubits=1,
        qiskit_builder=_single_qubit_circuit(lambda qc: qc.z(0)),
        cirq_builder=_cirq_single(cirq.Z),
    ),
    "H": GateDefinition(
        name="Hadamard",
        category="Superposition & Mixing",
        description="Creates equal superposition of |0> and |1>.",
        qubits=1,
        qiskit_builder=_single_qubit_circuit(lambda qc: qc.h(0)),
        cirq_builder=_cirq_single(cirq.H),
    ),
    "S": GateDefinition(
        name="Phase",
        category="Superposition & Mixing",
        description="Applies a 90-degree phase shift (square root of Z).",
        qubits=1,
        qiskit_builder=_single_qubit_circuit(lambda qc: qc.s(0)),
        cirq_builder=_cirq_single(cirq.S),
    ),
    "T": GateDefinition(
        name="T (pi/8)",
        category="Superposition & Mixing",
        description="Applies a 45-degree phase shift (square root of S).",
        qubits=1,
        qiskit_builder=_single_qubit_circuit(lambda qc: qc.t(0)),
        cirq_builder=_cirq_single(cirq.T),
    ),
    "SX": GateDefinition(
        name="Square-root of X",
        category="Superposition & Mixing",
        description="Applied twice equals X gate.",
        qubits=1,
        qiskit_builder=_single_qubit_circuit(lambda qc: qc.sx(0)),
        cirq_builder=_cirq_single(cirq.rx(math.pi / 2)),
    ),
    "SY": GateDefinition(
        name="Square-root of Y",
        category="Superposition & Mixing",
        description="Applied twice equals Y gate.",
        qubits=1,
        qiskit_builder=_single_qubit_circuit(lambda qc: qc.ry(math.pi / 4, 0)),
        cirq_builder=_cirq_single(cirq.ry(math.pi / 4)),
    ),
    "RX": GateDefinition(
        name="Rotation-X",
        category="Rotation",
        description="Rotates state around the X-axis by a configurable angle.",
        qubits=1,
        qiskit_builder=_single_qubit_circuit(lambda qc: qc.rx(math.pi / 3, 0)),
        cirq_builder=_cirq_single(cirq.rx(math.pi / 3)),
    ),
    "RY": GateDefinition(
        name="Rotation-Y",
        category="Rotation",
        description="Rotates state around the Y-axis by a configurable angle.",
        qubits=1,
        qiskit_builder=_single_qubit_circuit(lambda qc: qc.ry(math.pi / 3, 0)),
        cirq_builder=_cirq_single(cirq.ry(math.pi / 3)),
    ),
    "RZ": GateDefinition(
        name="Rotation-Z",
        category="Rotation",
        description="Rotates state around the Z-axis by a configurable angle.",
        qubits=1,
        qiskit_builder=_single_qubit_circuit(lambda qc: qc.rz(math.pi / 3, 0)),
        cirq_builder=_cirq_single(cirq.rz(math.pi / 3)),
    ),
    "U3": GateDefinition(
        name="U3 Universal Gate",
        category="Rotation",
        description="General single-qubit rotation parameterized by theta, phi, lambda.",
        qubits=1,
        qiskit_builder=_single_qubit_circuit(lambda qc: qc.u(1.2, 0.4, 0.7, 0)),
        cirq_builder=_cirq_single(
            cirq.PhasedXPowGate(phase_exponent=0.4 / math.pi, exponent=1.2 / math.pi)
        ),
    ),
    "CX": GateDefinition(
        name="Controlled-NOT",
        category="2-Qubit Controlled",
        description="Flips target qubit when control is |1>.",
        qubits=2,
        qiskit_builder=_two_qubit_circuit(lambda qc: qc.cx(0, 1)),
        cirq_builder=_cirq_two(cirq.CNOT),
    ),
    "CZ": GateDefinition(
        name="Controlled-Z",
        category="2-Qubit Controlled",
        description="Applies Z on target conditional on control.",
        qubits=2,
        qiskit_builder=_two_qubit_circuit(lambda qc: qc.cz(0, 1)),
        cirq_builder=_cirq_two(cirq.CZ),
    ),
    "CY": GateDefinition(
        name="Controlled-Y",
        category="2-Qubit Controlled",
        description="Applies Y on the target when the control qubit is 1.",
        qubits=2,
        qiskit_builder=_two_qubit_circuit(lambda qc: qc.cy(0, 1)),
        cirq_builder=lambda: cirq.Circuit(
            cirq.Y.on(cirq.LineQubit(1)).controlled_by(cirq.LineQubit(0)),
            cirq.measure(*cirq.LineQubit.range(2), key="m"),
        ),
    ),
    "CP": GateDefinition(
        name="Controlled-Phase",
        category="2-Qubit Controlled",
        description="Applies phase rotation conditional on control qubit.",
        qubits=2,
        qiskit_builder=_two_qubit_circuit(lambda qc: qc.cp(math.pi / 4, 0, 1)),
        cirq_builder=_cirq_two(cirq.CZPowGate(exponent=0.5)),
    ),
    "SWAP": GateDefinition(
        name="SWAP",
        category="Swap & Entanglement",
        description="Swaps the states of two qubits.",
        qubits=2,
        qiskit_builder=_two_qubit_circuit(lambda qc: qc.swap(0, 1)),
        cirq_builder=_cirq_two(cirq.SWAP),
    ),
    "iSWAP": GateDefinition(
        name="iSWAP",
        category="Swap & Entanglement",
        description="Swaps qubits with a complex phase factor.",
        qubits=2,
        qiskit_builder=_two_qubit_circuit(lambda qc: qc.iswap(0, 1)),
        cirq_builder=_cirq_two(cirq.ISWAP),
    ),
    "CSWAP": GateDefinition(
        name="Fredkin",
        category="3+ Qubit",
        description="Controlled swap of target qubits.",
        qubits=3,
        qiskit_builder=_three_qubit_circuit(lambda qc: qc.cswap(0, 1, 2)),
        cirq_builder=_cirq_three(cirq.FREDKIN),
    ),
    "CCX": GateDefinition(
        name="Toffoli",
        category="3+ Qubit",
        description="Doubles-controlled NOT gate.",
        qubits=3,
        qiskit_builder=_three_qubit_circuit(lambda qc: qc.ccx(0, 1, 2)),
        cirq_builder=_cirq_three(cirq.CCX),
    ),
    "MEASURE": GateDefinition(
        name="Measurement",
        category="Measurement & Reset",
        description="Measures qubits in the computational basis.",
        qubits=1,
        qiskit_builder=_single_qubit_circuit(lambda qc: None),
        cirq_builder=lambda: cirq.Circuit(cirq.measure(cirq.LineQubit(0), key="m0")),
    ),
}


def get_gate(name: str) -> GateDefinition:
    key = name.upper()
    if key not in GATE_LIBRARY:
        raise KeyError(f"Unknown gate '{name}'. Available: {', '.join(sorted(GATE_LIBRARY))}")
    return GATE_LIBRARY[key]


def categories() -> Dict[str, Dict[str, GateDefinition]]:
    groups: Dict[str, Dict[str, GateDefinition]] = {}
    for short_name, definition in GATE_LIBRARY.items():
        groups.setdefault(definition.category, {})[short_name] = definition
    return groups
