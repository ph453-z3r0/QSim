from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Optional

from qiskit import QuantumCircuit
import cirq


class CircuitLoadError(RuntimeError):
    """Raised when a circuit cannot be created from supplied source."""


def _read_code(source: Optional[Path], code: Optional[str], stdin: bool) -> str:
    provided = sum(bool(x) for x in (source, code, stdin))
    if provided != 1:
        raise ValueError("Exactly one of --source, --code, or --stdin must be provided.")

    if source:
        return source.read_text(encoding="utf-8")
    if code is not None:
        return code
    return sys.stdin.read()


def _execute(code: str, filename: str) -> Dict[str, Any]:
    namespace: Dict[str, Any] = {}
    exec(compile(code, filename, "exec"), namespace, namespace)
    return namespace


def _resolve_callable(namespace: Dict[str, Any], callable_name: Optional[str]) -> Optional[Any]:
    if not callable_name:
        return None
    target = namespace.get(callable_name)
    if target is None or not callable(target):
        raise CircuitLoadError(f"Callable '{callable_name}' not found or not callable.")
    return target()


def _resolve_instance(namespace: Dict[str, Any], backend: str) -> Optional[Any]:
    candidates = []
    for key in ("CIRCUIT", "circuit", "qc", "q_circuit", "build"):
        if key in namespace:
            candidates.append(namespace[key])

    # Fallback: search namespace values
    candidates.extend(namespace.values())

    if backend == "qiskit":
        for value in candidates:
            if isinstance(value, QuantumCircuit):
                return value
    else:
        for value in candidates:
            if isinstance(value, cirq.Circuit):
                return value
    return None


def load_circuit(
    *,
    backend: str,
    source: Optional[Path] = None,
    code: Optional[str] = None,
    stdin: bool = False,
    callable_name: Optional[str] = None,
) -> Any:
    """Load a circuit object by executing user-supplied code."""
    code_str = _read_code(source, code, stdin)
    filename = str(source) if source else ("<stdin>" if stdin else "<snippet>")
    namespace = _execute(code_str, filename)

    obj = _resolve_callable(namespace, callable_name)
    if obj is None:
        obj = _resolve_instance(namespace, backend)

    if backend == "qiskit":
        if not isinstance(obj, QuantumCircuit):
            raise CircuitLoadError(
                "Supplied code did not produce a qiskit.QuantumCircuit instance. "
                "Define a function returning the circuit and pass --callable, "
                "set a variable named 'CIRCUIT', or ensure the last expression "
                "evaluates to the circuit."
            )
    else:
        if not isinstance(obj, cirq.Circuit):
            raise CircuitLoadError(
                "Supplied code did not produce a cirq.Circuit instance. "
                "Define a function returning the circuit and pass --callable, "
                "set a variable named 'CIRCUIT', or ensure the last expression "
                "evaluates to the circuit."
            )
    return obj


