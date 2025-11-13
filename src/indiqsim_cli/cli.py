from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable, List

from .analysis import analyse_qiskit_circuit, analyse_cirq_circuit
from .exporters import export_qiskit_circuit, export_cirq_circuit, SUPPORTED_FORMATS
from .loader import load_circuit, CircuitLoadError
from .visualizations import create_comprehensive_report


def _add_source_arguments(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--source", type=Path, help="Path to a Python file containing circuit-building code.")
    group.add_argument("--code", type=str, help="Inline Python snippet that builds the circuit.")
    group.add_argument(
        "--stdin",
        action="store_true",
        help="Read Python code from standard input. Useful for piping scripts directly.",
    )
    parser.add_argument(
        "--callable",
        type=str,
        help="Optional callable name in the supplied code that returns the circuit (e.g., build_circuit).",
    )


def _format_analysis_text(result, label: str | None = None) -> str:
    lines = []
    if label:
        lines.append(label)
    lines.extend(
        [
            f"Backend: {result.backend}",
            f"Qubits: {result.qubits}",
            f"Depth: {result.depth}",
            f"Operations: {result.operations}",
            f"Operations by type: {result.operations_by_type}",
            f"Measurements: {result.measurements}",
            f"Has measurements: {result.has_measurements}",
        ]
    )
    
    # Add state vector information
    if result.state_vector:
        lines.append("")
        lines.append("State Vector:")
        for i, amplitude in enumerate(result.state_vector):
            # Only show non-negligible amplitudes
            if abs(amplitude) > 1e-10:
                real_part = amplitude.real
                imag_part = amplitude.imag
                if abs(imag_part) < 1e-10:
                    # Real number only
                    lines.append(f"  |{format(i, f'0{result.qubits}b')}>: {real_part:.6f}")
                elif abs(real_part) < 1e-10:
                    # Pure imaginary
                    lines.append(f"  |{format(i, f'0{result.qubits}b')}>: {imag_part:.6f}j")
                else:
                    # Complex number
                    sign = "+" if imag_part >= 0 else "-"
                    lines.append(f"  |{format(i, f'0{result.qubits}b')}>: {real_part:.6f} {sign} {abs(imag_part):.6f}j")
    
    # Add probabilities
    if result.probabilities:
        lines.append("")
        lines.append("Probabilities:")
        # Sort by probability (descending)
        sorted_probs = sorted(result.probabilities.items(), key=lambda x: x[1], reverse=True)
        for basis_state, prob in sorted_probs:
            percentage = prob * 100
            lines.append(f"  |{basis_state}>: {prob:.6f} ({percentage:.2f}%)")
    
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="indiqsim-cli",
        description="Execute user-supplied Qiskit or Cirq code and export circuits as PNG/SVG/QASM with analysis.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    export_parser = subparsers.add_parser("export", help="Export a custom circuit to PNG/SVG/QASM.")
    export_parser.add_argument("--backend", choices=["qiskit", "cirq"], required=True)
    export_parser.add_argument(
        "--format",
        action="append",
        dest="formats",
        required=True,
        help=f"Export format. Supported: {', '.join(sorted(SUPPORTED_FORMATS))}. Can be passed multiple times. "
             f"Formats: png, svg (diagrams), qasm (OpenQASM), qiskit_python, cirq_python (code), "
             f"json (descriptions), pdf (reports), latex (academic), javascript (web).",
    )
    export_parser.add_argument("--output", type=Path, default=Path("exports"), help="Destination directory.")
    export_parser.add_argument(
        "--analysis-format",
        choices=["text", "json", "comprehensive"],
        default="text",
        help="How to print analysis metrics after exporting. 'comprehensive' includes all visualizations.",
    )
    _add_source_arguments(export_parser)

    analyze_parser = subparsers.add_parser("analyze", help="Analyse a custom circuit and print metrics.")
    analyze_parser.add_argument("--backend", choices=["qiskit", "cirq"], required=True)
    analyze_parser.add_argument("--format", choices=["text", "json", "comprehensive"], default="text")
    analyze_parser.add_argument("--output", type=Path, help="Optional: Save analysis report to a file in this directory.")
    _add_source_arguments(analyze_parser)

    return parser


def _analyze_circuit(backend: str, circuit) -> str:
    if backend == "qiskit":
        return analyse_qiskit_circuit(circuit)
    return analyse_cirq_circuit(circuit)


def _load_user_circuit(args) -> object:
    return load_circuit(
        backend=args.backend,
        source=getattr(args, "source", None),
        code=getattr(args, "code", None),
        stdin=getattr(args, "stdin", False),
        callable_name=getattr(args, "callable", None),
    )


def _print_analysis(result, output_format: str, label: str | None = None, save_to_file: Path | None = None) -> None:
    if output_format == "json":
        payload = result.to_dict()
        if label:
            payload = {"label": label, **payload}
        content = json.dumps(payload, indent=2)
    elif output_format == "comprehensive":
        content = create_comprehensive_report(result)
    else:
        content = _format_analysis_text(result, label)
    
    # Print to console
    print(content)
    
    # Save to file if requested
    if save_to_file:
        save_to_file.parent.mkdir(parents=True, exist_ok=True)
        save_to_file.write_text(content, encoding="utf-8")
        print(f"\nAnalysis report saved to: {save_to_file}")


def main(argv: Iterable[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        circuit = _load_user_circuit(args)
    except (CircuitLoadError, ValueError) as exc:
        parser.error(str(exc))

    if args.command == "export":
        if args.backend == "qiskit":
            paths = export_qiskit_circuit(circuit, args.output, "custom_circuit", args.formats)
        else:
            paths = export_cirq_circuit(circuit, args.output, "custom_circuit", args.formats)

        for path in paths:
            print(path)

        analysis = _analyze_circuit(args.backend, circuit)
        # Save analysis report to file in output directory
        if args.analysis_format == "json":
            report_ext = "json"
        elif args.analysis_format == "comprehensive":
            report_ext = "txt"
        else:
            report_ext = "txt"
        report_path = args.output / f"custom_circuit_analysis.{report_ext}"
        _print_analysis(analysis, args.analysis_format, label="Analysis", save_to_file=report_path)
        return 0

    if args.command == "analyze":
        analysis = _analyze_circuit(args.backend, circuit)
        # Save to file if output directory is specified
        report_path = None
        if args.output:
            if args.format == "json":
                report_ext = "json"
            else:
                report_ext = "txt"
            report_path = args.output / f"circuit_analysis.{report_ext}"
        _print_analysis(analysis, args.format, save_to_file=report_path)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

