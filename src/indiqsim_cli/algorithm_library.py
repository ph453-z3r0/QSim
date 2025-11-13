from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List
import math

from qiskit import QuantumCircuit
import cirq


@dataclass(frozen=True)
class AlgorithmTemplate:
    """Metadata for a reusable algorithm template."""

    name: str
    description: str
    category: str
    tags: List[str]
    qiskit_builder: Callable[[], QuantumCircuit]
    cirq_builder: Callable[[], cirq.Circuit]


def _measure_all(qc: QuantumCircuit) -> QuantumCircuit:
    qc.barrier()
    qc.measure_all(add_bits=False)
    return qc


def _grover_qiskit() -> QuantumCircuit:
    qc = QuantumCircuit(2)
    qc.h([0, 1])
    qc.cz(0, 1)
    qc.h([0, 1])
    qc.z([0, 1])
    qc.cz(0, 1)
    _measure_all(qc)
    return qc


def _grover_cirq() -> cirq.Circuit:
    q0, q1 = cirq.LineQubit.range(2)
    return cirq.Circuit(
        cirq.H(q0),
        cirq.H(q1),
        cirq.CZ(q0, q1),
        cirq.H(q0),
        cirq.H(q1),
        cirq.Z(q0),
        cirq.Z(q1),
        cirq.CZ(q0, q1),
        cirq.measure(q0, q1, key="m"),
    )


def _qft_qiskit(num_qubits: int = 3) -> QuantumCircuit:
    qc = QuantumCircuit(num_qubits)
    for j in range(num_qubits):
        qc.h(j)
        for k in range(j + 1, num_qubits):
            qc.cp(math.pi / 2 ** (k - j), k, j)
    qc.swap(0, num_qubits - 1)
    _measure_all(qc)
    return qc


def _qft_cirq(num_qubits: int = 3) -> cirq.Circuit:
    qubits = cirq.LineQubit.range(num_qubits)
    ops = []
    for j, q in enumerate(qubits):
        ops.append(cirq.H(q))
        for k in range(j + 1, num_qubits):
            angle = math.pi / 2 ** (k - j)
            ops.append(cirq.CZPowGate(exponent=angle / math.pi)(qubits[k], q))
    ops.append(cirq.SWAP(qubits[0], qubits[-1]))
    ops.append(cirq.measure(*qubits, key="m"))
    return cirq.Circuit(*ops)


def _teleport_qiskit() -> QuantumCircuit:
    qc = QuantumCircuit(3, 3)
    qc.h(1)
    qc.cx(1, 2)
    qc.cx(0, 1)
    qc.h(0)
    qc.measure(0, 0)
    qc.measure(1, 1)
    qc.barrier()
    qc.cz(1, 2)
    qc.cx(0, 2)
    qc.measure(2, 2)
    return qc


def _teleport_cirq() -> cirq.Circuit:
    q0, q1, q2 = cirq.LineQubit.range(3)
    return cirq.Circuit(
        cirq.H(q1),
        cirq.CNOT(q1, q2),
        cirq.CNOT(q0, q1),
        cirq.H(q0),
        cirq.measure(q0, key="m0"),
        cirq.measure(q1, key="m1"),
        cirq.CZPowGate(exponent=1)(q1, q2),
        cirq.CNOT(q0, q2),
        cirq.measure(q2, key="m2"),
    )


def _bb84_qiskit() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc


def _bb84_cirq() -> cirq.Circuit:
    q0, q1 = cirq.LineQubit.range(2)
    return cirq.Circuit(
        cirq.H(q0),
        cirq.CNOT(q0, q1),
        cirq.measure(q0, q1, key="m"),
    )


def _deutsch_jozsa_qiskit() -> QuantumCircuit:
    qc = QuantumCircuit(2)
    qc.h([0, 1])
    qc.x(1)
    qc.h(1)
    qc.cz(0, 1)
    qc.h(0)
    _measure_all(qc)
    return qc


def _deutsch_jozsa_cirq() -> cirq.Circuit:
    q0, q1 = cirq.LineQubit.range(2)
    return cirq.Circuit(
        cirq.H.on_each(q0, q1),
        cirq.X(q1),
        cirq.H(q1),
        cirq.CZ(q0, q1),
        cirq.H(q0),
        cirq.measure(q0, q1, key="m"),
    )


def _bitflip_code_qiskit() -> QuantumCircuit:
    qc = QuantumCircuit(3)
    qc.cx(0, 1)
    qc.cx(0, 2)
    qc.barrier()
    qc.cx(1, 0)
    qc.cx(2, 0)
    _measure_all(qc)
    return qc


def _bitflip_code_cirq() -> cirq.Circuit:
    q0, q1, q2 = cirq.LineQubit.range(3)
    return cirq.Circuit(
        cirq.CNOT(q0, q1),
        cirq.CNOT(q0, q2),
        cirq.CNOT(q1, q0),
        cirq.CNOT(q2, q0),
        cirq.measure(q0, q1, q2, key="m"),
    )


def _vqe_ansatz_qiskit() -> QuantumCircuit:
    qc = QuantumCircuit(2)
    theta = math.pi / 4
    qc.ry(theta, 0)
    qc.ry(theta, 1)
    qc.cx(0, 1)
    qc.rz(theta / 2, 1)
    qc.cx(0, 1)
    _measure_all(qc)
    return qc


def _vqe_ansatz_cirq() -> cirq.Circuit:
    q0, q1 = cirq.LineQubit.range(2)
    theta = math.pi / 4
    return cirq.Circuit(
        cirq.ry(theta)(q0),
        cirq.ry(theta)(q1),
        cirq.CNOT(q0, q1),
        cirq.rz(theta / 2)(q1),
        cirq.CNOT(q0, q1),
        cirq.measure(q0, q1, key="m"),
    )


ALGORITHM_LIBRARY: Dict[str, AlgorithmTemplate] = {
    "grover": AlgorithmTemplate(
        name="Grover Search",
        description="Two-qubit Grover search demonstration with oracle and diffusion steps.",
        category="Search",
        tags=["education", "analysis"],
        qiskit_builder=_grover_qiskit,
        cirq_builder=_grover_cirq,
    ),
    "qft": AlgorithmTemplate(
        name="Quantum Fourier Transform",
        description="Three-qubit QFT highlighting controlled-phase rotations.",
        category="Fourier & Phase",
        tags=["analysis", "template"],
        qiskit_builder=_qft_qiskit,
        cirq_builder=_qft_cirq,
    ),
    "teleport": AlgorithmTemplate(
        name="Quantum Teleportation",
        description="Standard teleportation protocol with measurement and classical feed-forward.",
        category="Communication",
        tags=["education", "template"],
        qiskit_builder=_teleport_qiskit,
        cirq_builder=_teleport_cirq,
    ),
    "bb84": AlgorithmTemplate(
        name="BB84 Key Distribution",
        description="Illustrative circuit for sharing a BB84 key element.",
        category="Communication",
        tags=["security", "education"],
        qiskit_builder=_bb84_qiskit,
        cirq_builder=_bb84_cirq,
    ),
    "deutsch_jozsa": AlgorithmTemplate(
        name="Deutsch-Jozsa",
        description="Two-qubit example contrasting constant vs balanced oracles.",
        category="Decision",
        tags=["education"],
        qiskit_builder=_deutsch_jozsa_qiskit,
        cirq_builder=_deutsch_jozsa_cirq,
    ),
    "bitflip_code": AlgorithmTemplate(
        name="Three-Qubit Bit Flip Code",
        description="Basic quantum error-correcting code illustrating redundancy.",
        category="Error Correction",
        tags=["analysis", "template"],
        qiskit_builder=_bitflip_code_qiskit,
        cirq_builder=_bitflip_code_cirq,
    ),
    "vqe_ansatz": AlgorithmTemplate(
        name="VQE Ansatz",
        description="Minimal two-qubit parametrized circuit suitable for VQE demonstrations.",
        category="Variational",
        tags=["analysis", "optimization"],
        qiskit_builder=_vqe_ansatz_qiskit,
        cirq_builder=_vqe_ansatz_cirq,
    ),
}


def get_algorithm(key: str) -> AlgorithmTemplate:
    normalized = key.lower()
    if normalized not in ALGORITHM_LIBRARY:
        raise KeyError(f"Unknown algorithm '{key}'. Available: {', '.join(sorted(ALGORITHM_LIBRARY))}")
    return ALGORITHM_LIBRARY[normalized]


def categories() -> Dict[str, List[AlgorithmTemplate]]:
    grouped: Dict[str, List[AlgorithmTemplate]] = {}
    for template in ALGORITHM_LIBRARY.values():
        grouped.setdefault(template.category, []).append(template)
    return grouped
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List

import math

from qiskit import QuantumCircuit
import cirq


@dataclass(frozen=True)
class AlgorithmTemplate:
    """Metadata for an algorithm template with circuit builders."""

    name: str
    description: str
    category: str
    tags: List[str]
    qiskit_builder: Callable[[], QuantumCircuit]
    cirq_builder: Callable[[], cirq.Circuit]


def _default_measure(qc: QuantumCircuit) -> QuantumCircuit:
    qc.barrier()
    qc.measure_all(add_bits=False)
    return qc


def _grover_qiskit() -> QuantumCircuit:
    qc = QuantumCircuit(2)
    qc.h([0, 1])
    qc.cz(0, 1)
    qc.h([0, 1])
    qc.z([0, 1])
    qc.cz(0, 1)
    _default_measure(qc)
    return qc


def _grover_cirq() -> cirq.Circuit:
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(
        cirq.H(q0),
        cirq.H(q1),
        cirq.CZ(q0, q1),
        cirq.H(q0),
        cirq.H(q1),
        cirq.Z(q0),
        cirq.Z(q1),
        cirq.CZ(q0, q1),
        cirq.measure(q0, q1, key="m"),
    )
    return circuit


def _qft_qiskit(num_qubits: int = 3) -> QuantumCircuit:
    qc = QuantumCircuit(num_qubits)
    for j in range(num_qubits):
        qc.h(j)
        for k in range(j + 1, num_qubits):
            qc.cp(math.pi / 2 ** (k - j), k, j)
    qc.swap(0, num_qubits - 1)
    _default_measure(qc)
    return qc


def _qft_cirq(num_qubits: int = 3) -> cirq.Circuit:
    qubits = cirq.LineQubit.range(num_qubits)
    ops = []
    for j, q in enumerate(qubits):
        ops.append(cirq.H(q))
        for k in range(j + 1, num_qubits):
            angle = math.pi / 2 ** (k - j)
            ops.append(cirq.CZPowGate(exponent=angle / math.pi)(qubits[k], q))
    ops.append(cirq.SWAP(qubits[0], qubits[-1]))
    ops.append(cirq.measure(*qubits, key="m"))
    return cirq.Circuit(*ops)


def _teleport_qiskit() -> QuantumCircuit:
    qc = QuantumCircuit(3)
    qc.h(1)
    qc.cx(1, 2)
    qc.cx(0, 1)
    qc.h(0)
    qc.measure([0, 1], [0, 1])
    qc.cz(1, 2)
    qc.cx(0, 2)
    qc.barrier()
    qc.measure(2, 2)
    return qc


def _teleport_cirq() -> cirq.Circuit:
    q0, q1, q2 = cirq.LineQubit.range(3)
    circuit = cirq.Circuit(
        cirq.H(q1),
        cirq.CNOT(q1, q2),
        cirq.CNOT(q0, q1),
        cirq.H(q0),
        cirq.measure(q0, key="m0"),
        cirq.measure(q1, key="m1"),
        cirq.CZPowGate(exponent=1.0)(q1, q2),
        cirq.CNOT(q0, q2),
        cirq.measure(q2, key="m2"),
    )
    return circuit


def _bb84_qiskit() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.barrier()
    qc.measure([0, 1], [0, 1])
    return qc


def _bb84_cirq() -> cirq.Circuit:
    q0, q1 = cirq.LineQubit.range(2)
    return cirq.Circuit(
        cirq.H(q0),
        cirq.CX(q0, q1),
        cirq.measure(q0, q1, key="m"),
    )


def _deutsch_jozsa_qiskit() -> QuantumCircuit:
    qc = QuantumCircuit(2)
    qc.h([0, 1])
    qc.x(1)
    qc.h(1)
    qc.cz(0, 1)
    qc.h(0)
    _default_measure(qc)
    return qc


def _deutsch_jozsa_cirq() -> cirq.Circuit:
    q0, q1 = cirq.LineQubit.range(2)
    return cirq.Circuit(
        cirq.H.on_each(q0, q1),
        cirq.X(q1),
        cirq.H(q1),
        cirq.CZ(q0, q1),
        cirq.H(q0),
        cirq.measure(q0, q1, key="m"),
    )


def _bitflip_code_qiskit() -> QuantumCircuit:
    qc = QuantumCircuit(3)
    qc.cx(0, 1)
    qc.cx(0, 2)
    qc.barrier()
    qc.cx(1, 0)
    qc.cx(2, 0)
    _default_measure(qc)
    return qc


def _bitflip_code_cirq() -> cirq.Circuit:
    q0, q1, q2 = cirq.LineQubit.range(3)
    return cirq.Circuit(
        cirq.CNOT(q0, q1),
        cirq.CNOT(q0, q2),
        cirq.CNOT(q1, q0),
        cirq.CNOT(q2, q0),
        cirq.measure(q0, q1, q2, key="m"),
    )


def _vqe_ansatz_qiskit() -> QuantumCircuit:
    qc = QuantumCircuit(2)
    theta = math.pi / 4
    qc.ry(theta, 0)
    qc.ry(theta, 1)
    qc.cx(0, 1)
    qc.rz(theta / 2, 1)
    qc.cx(0, 1)
    _default_measure(qc)
    return qc


def _vqe_ansatz_cirq() -> cirq.Circuit:
    q0, q1 = cirq.LineQubit.range(2)
    theta = math.pi / 4
    return cirq.Circuit(
        cirq.ry(theta)(q0),
        cirq.ry(theta)(q1),
        cirq.CNOT(q0, q1),
        cirq.rz(theta / 2)(q1),
        cirq.CNOT(q0, q1),
        cirq.measure(q0, q1, key="m"),
    )


ALGORITHM_LIBRARY: Dict[str, AlgorithmTemplate] = {
    "grover": AlgorithmTemplate(
        name="Grover Search",
        description="Two-qubit Grover search iterating a single oracle and diffusion step.",
        category="Quantum Search",
        tags=["education", "analysis"],
        qiskit_builder=_grover_qiskit,
        cirq_builder=_grover_cirq,
    ),
    "qft": AlgorithmTemplate(
        name="Quantum Fourier Transform",
        description="Three-qubit QFT with controlled-phase rotations.",
        category="Fourier & Phase",
        tags=["analysis", "template"],
        qiskit_builder=_qft_qiskit,
        cirq_builder=_qft_cirq,
    ),
    "teleport": AlgorithmTemplate(
        name="Quantum Teleportation",
        description="Standard three-qubit teleportation protocol with classical feed-forward gates represented implicitly.",
        category="Communication",
        tags=["education", "bb84", "template"],
        qiskit_builder=_teleport_qiskit,
        cirq_builder=_teleport_cirq,
    ),
    "bb84": AlgorithmTemplate(
        name="BB84 Key Distribution",
        description="Illustrative two-qubit circuit encoding and sharing a BB84 key element.",
        category="Communication",
        tags=["security", "education"],
        qiskit_builder=_bb84_qiskit,
        cirq_builder=_bb84_cirq,
    ),
    "deutsch_jozsa": AlgorithmTemplate(
        name="Deutsch-Jozsa",
        description="Constant vs balanced oracle example using controlled-Z as balanced function.",
        category="Decision",
        tags=["education"],
        qiskit_builder=_deutsch_jozsa_qiskit,
        cirq_builder=_deutsch_jozsa_cirq,
    ),
    "bitflip_code": AlgorithmTemplate(
        name="Three-Qubit Bit Flip Code",
        description="Basic quantum error-correcting code encoding and partial correction flow.",
        category="Error Correction",
        tags=["analysis", "template"],
        qiskit_builder=_bitflip_code_qiskit,
        cirq_builder=_bitflip_code_cirq,
    ),
    "vqe_ansatz": AlgorithmTemplate(
        name="VQE Hardware-Efficient Ansatz",
        description="Minimal two-qubit parameterized circuit for VQE-style optimisation.",
        category="Variational",
        tags=["analysis", "optimization"],
        qiskit_builder=_vqe_ansatz_qiskit,
        cirq_builder=_vqe_ansatz_cirq,
    ),
}


def get_algorithm(key: str) -> AlgorithmTemplate:
    normalized = key.lower()
    if normalized not in ALGORITHM_LIBRARY:
        raise KeyError(f"Unknown algorithm '{key}'. Available: {', '.join(sorted(ALGORITHM_LIBRARY))}")
    return ALGORITHM_LIBRARY[normalized]


def categories() -> Dict[str, List[AlgorithmTemplate]]:
    groups: Dict[str, List[AlgorithmTemplate]] = {}
    for template in ALGORITHM_LIBRARY.values():
        groups.setdefault(template.category, []).append(template)
    return groups
