from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
import numpy as np

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
import cirq


@dataclass(frozen=True)
class CircuitAnalysis:
    backend: str
    qubits: int
    depth: int
    operations: int
    operations_by_type: Dict[str, int]
    state_vector: Optional[List[complex]] = None
    probabilities: Optional[Dict[str, float]] = None
    measurements: int = 0
    has_measurements: bool = False

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        # Convert complex numbers to strings for JSON serialization
        if result.get("state_vector"):
            result["state_vector"] = [
                {"real": float(c.real), "imag": float(c.imag)} for c in result["state_vector"]
            ]
        return result


def analyse_qiskit_circuit(circuit: QuantumCircuit) -> CircuitAnalysis:
    ops_by_type = {name: int(count) for name, count in circuit.count_ops().items()}
    
    # Count measurements
    measurements = ops_by_type.get("measure", 0)
    has_measurements = measurements > 0
    
    # Get state vector and probabilities (remove measurements for state vector calculation)
    state_vector = None
    probabilities = None
    
    try:
        # Create a copy without measurements for state vector calculation
        circuit_no_measure = circuit.remove_final_measurements(inplace=False)
        state = Statevector.from_instruction(circuit_no_measure)
        state_vector = state.data.tolist()
        
        # Calculate probabilities for each basis state
        probs = state.probabilities()
        probabilities = {}
        num_qubits = circuit_no_measure.num_qubits
        for i, prob in enumerate(probs):
            if prob > 1e-10:  # Only include non-negligible probabilities
                basis_state = format(i, f"0{num_qubits}b")
                probabilities[basis_state] = float(prob)
    except Exception:
        # If state vector calculation fails, continue without it
        pass
    
    return CircuitAnalysis(
        backend="qiskit",
        qubits=circuit.num_qubits,
        depth=circuit.depth(),
        operations=circuit.size(),
        operations_by_type=ops_by_type,
        state_vector=state_vector,
        probabilities=probabilities,
        measurements=measurements,
        has_measurements=has_measurements,
    )


def analyse_cirq_circuit(circuit: cirq.Circuit) -> CircuitAnalysis:
    ops_by_type: Dict[str, int] = {}
    measurements = 0
    for op in circuit.all_operations():
        key = op.gate.__class__.__name__ if isinstance(op, cirq.GateOperation) else type(op).__name__
        ops_by_type[key] = ops_by_type.get(key, 0) + 1
        # Check if it's a measurement operation
        if isinstance(op, cirq.ops.GateOperation) and isinstance(op.gate, cirq.ops.MeasurementGate):
            measurements += 1
        elif "measure" in key.lower():
            measurements += 1
    
    has_measurements = measurements > 0
    
    # Get state vector and probabilities
    state_vector = None
    probabilities = None
    
    try:
        # Create a circuit without measurements for state vector calculation
        circuit_no_measure = cirq.Circuit()
        for moment in circuit:
            for op in moment:
                # Skip measurement operations
                is_measurement = (
                    isinstance(op, cirq.ops.GateOperation) and isinstance(op.gate, cirq.ops.MeasurementGate)
                ) or "measure" in (op.gate.__class__.__name__ if isinstance(op, cirq.GateOperation) else type(op).__name__).lower()
                if not is_measurement:
                    circuit_no_measure.append(op)
        
        # Simulate to get state vector
        simulator = cirq.Simulator()
        result = simulator.simulate(circuit_no_measure)
        state_vector = result.state_vector().tolist()
        
        # Calculate probabilities
        probs = np.abs(result.state_vector()) ** 2
        probabilities = {}
        num_qubits = len(circuit.all_qubits())
        for i, prob in enumerate(probs):
            if prob > 1e-10:  # Only include non-negligible probabilities
                basis_state = format(i, f"0{num_qubits}b")
                probabilities[basis_state] = float(prob)
    except Exception:
        # If state vector calculation fails, continue without it
        pass
    
    return CircuitAnalysis(
        backend="cirq",
        qubits=len(circuit.all_qubits()),
        depth=circuit.depth(),
        operations=sum(ops_by_type.values()),
        operations_by_type=ops_by_type,
        state_vector=state_vector,
        probabilities=probabilities,
        measurements=measurements,
        has_measurements=has_measurements,
    )

