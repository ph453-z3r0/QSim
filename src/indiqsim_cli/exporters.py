from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence, Set, Optional
import json
import re

import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
import cirq

SUPPORTED_FORMATS: Set[str] = {
    "png", "svg", "qasm", "qiskit_python", "cirq_python", 
    "json", "pdf", "latex", "javascript"
}


def _normalize_formats(formats: Iterable[str]) -> Sequence[str]:
    normalized = []
    for fmt in formats:
        lower = fmt.lower()
        if lower not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported export format '{fmt}'. Supported: {', '.join(sorted(SUPPORTED_FORMATS))}")
        if lower not in normalized:
            normalized.append(lower)
    return normalized


def _circuit_to_qiskit_python(circuit: QuantumCircuit) -> str:
    """Convert Qiskit circuit to Python code string."""
    lines = ["from qiskit import QuantumCircuit", ""]
    lines.append(f"qc = QuantumCircuit({circuit.num_qubits})")
    
    for instruction in circuit.data:
        gate_name = instruction.operation.name
        qubits = [circuit.find_bit(q).index for q in instruction.qubits]
        
        if gate_name == "h":
            lines.append(f"qc.h({qubits[0]})")
        elif gate_name == "x":
            lines.append(f"qc.x({qubits[0]})")
        elif gate_name == "y":
            lines.append(f"qc.y({qubits[0]})")
        elif gate_name == "z":
            lines.append(f"qc.z({qubits[0]})")
        elif gate_name == "cx":
            lines.append(f"qc.cx({qubits[0]}, {qubits[1]})")
        elif gate_name == "cz":
            lines.append(f"qc.cz({qubits[0]}, {qubits[1]})")
        elif gate_name == "cy":
            lines.append(f"qc.cy({qubits[0]}, {qubits[1]})")
        elif gate_name == "swap":
            lines.append(f"qc.swap({qubits[0]}, {qubits[1]})")
        elif gate_name == "ccx":
            lines.append(f"qc.ccx({qubits[0]}, {qubits[1]}, {qubits[2]})")
        elif gate_name == "cswap":
            lines.append(f"qc.cswap({qubits[0]}, {qubits[1]}, {qubits[2]})")
        elif gate_name == "s":
            lines.append(f"qc.s({qubits[0]})")
        elif gate_name == "sdg":
            lines.append(f"qc.sdg({qubits[0]})")
        elif gate_name == "t":
            lines.append(f"qc.t({qubits[0]})")
        elif gate_name == "tdg":
            lines.append(f"qc.tdg({qubits[0]})")
        elif gate_name == "rx":
            params = instruction.operation.params
            lines.append(f"qc.rx({params[0]}, {qubits[0]})")
        elif gate_name == "ry":
            params = instruction.operation.params
            lines.append(f"qc.ry({params[0]}, {qubits[0]})")
        elif gate_name == "rz":
            params = instruction.operation.params
            lines.append(f"qc.rz({params[0]}, {qubits[0]})")
        else:
            # Generic gate
            qubit_str = ", ".join(map(str, qubits))
            lines.append(f"qc.append({gate_name}(), [{qubit_str}])")
    
    lines.append("")
    lines.append("return qc")
    return "\n".join(lines)


def _circuit_to_json(circuit: QuantumCircuit) -> dict:
    """Convert circuit to JSON representation."""
    data = {
        "num_qubits": circuit.num_qubits,
        "num_clbits": circuit.num_clbits,
        "instructions": []
    }
    
    for instruction in circuit.data:
        gate_info = {
            "name": instruction.operation.name,
            "qubits": [circuit.find_bit(q).index for q in instruction.qubits],
            "clbits": [circuit.find_bit(c).index for c in instruction.clbits],
        }
        
        if hasattr(instruction.operation, "params") and instruction.operation.params:
            gate_info["params"] = [float(p) for p in instruction.operation.params]
        
        data["instructions"].append(gate_info)
    
    return data


def _circuit_to_latex(circuit: QuantumCircuit) -> str:
    """Convert circuit to LaTeX code using qcircuit package."""
    lines = [
        "\\documentclass{article}",
        "\\usepackage{qcircuit}",
        "\\begin{document}",
        "",
        "\\Qcircuit @C=1em @R=.7em {"
    ]
    
    num_qubits = circuit.num_qubits
    depth = circuit.depth()
    
    # Create wire structure
    for q in range(num_qubits):
        wire_parts = []
        for layer in range(depth):
            wire_parts.append("\\qw")
        lines.append(f"  \\lstick{{q_{q}}} & {' & '.join(wire_parts)} & \\qw \\\\")
    
    lines.append("}")
    lines.append("\\end{document}")
    
    return "\n".join(lines)


def _circuit_to_javascript(circuit: QuantumCircuit) -> str:
    """Convert circuit to JavaScript code."""
    lines = [
        "// Quantum Circuit in JavaScript",
        "// Requires a quantum circuit library",
        "",
        "const circuit = {",
        f'  numQubits: {circuit.num_qubits},',
        "  gates: ["
    ]
    
    for instruction in circuit.data:
        gate_name = instruction.operation.name
        qubits = [circuit.find_bit(q).index for q in instruction.qubits]
        
        gate_obj = {
            "name": gate_name,
            "qubits": qubits
        }
        
        if hasattr(instruction.operation, "params") and instruction.operation.params:
            gate_obj["params"] = [float(p) for p in instruction.operation.params]
        
        lines.append(f"    {json.dumps(gate_obj)},")
    
    lines.append("  ]")
    lines.append("};")
    lines.append("")
    lines.append("export default circuit;")
    
    return "\n".join(lines)


def export_qiskit_circuit(
    circuit: QuantumCircuit, 
    destination: Path, 
    base_name: str, 
    formats: Iterable[str],
    analysis_text: Optional[str] = None
) -> Sequence[Path]:
    destination.mkdir(parents=True, exist_ok=True)
    formats = _normalize_formats(formats)
    exported: list[Path] = []

    # OpenQASM
    if "qasm" in formats:
        qasm_path = destination / f"{base_name}.qasm"
        try:
            from qiskit import qasm2
            qasm_str = qasm2.dumps(circuit)
        except ImportError:
            try:
                qasm_str = circuit.qasm()
            except AttributeError:
                from qiskit.qasm import qasm
                qasm_str = qasm(circuit)
        qasm_path.write_text(qasm_str, encoding="utf-8")
        exported.append(qasm_path)

    # Qiskit Python code
    if "qiskit_python" in formats:
        python_path = destination / f"{base_name}_qiskit.py"
        python_code = _circuit_to_qiskit_python(circuit)
        python_path.write_text(python_code, encoding="utf-8")
        exported.append(python_path)

    # JSON circuit description
    if "json" in formats:
        json_path = destination / f"{base_name}.json"
        circuit_json = _circuit_to_json(circuit)
        json_path.write_text(json.dumps(circuit_json, indent=2), encoding="utf-8")
        exported.append(json_path)

    # LaTeX
    if "latex" in formats:
        latex_path = destination / f"{base_name}.tex"
        latex_code = _circuit_to_latex(circuit)
        latex_path.write_text(latex_code, encoding="utf-8")
        exported.append(latex_path)

    # JavaScript
    if "javascript" in formats:
        js_path = destination / f"{base_name}.js"
        js_code = _circuit_to_javascript(circuit)
        js_path.write_text(js_code, encoding="utf-8")
        exported.append(js_path)

    # PNG and SVG (visual diagrams)
    if any(fmt in {"png", "svg", "pdf"} for fmt in formats):
        fig = circuit.draw(output="mpl")
        if "png" in formats:
            png_path = destination / f"{base_name}.png"
            fig.savefig(png_path, format="png", dpi=300, bbox_inches="tight")
            exported.append(png_path)
        if "svg" in formats:
            svg_path = destination / f"{base_name}.svg"
            fig.savefig(svg_path, format="svg", bbox_inches="tight")
            exported.append(svg_path)
        if "pdf" in formats:
            pdf_path = destination / f"{base_name}.pdf"
            # If analysis text is provided, create a PDF report
            if analysis_text:
                try:
                    from reportlab.lib.pagesizes import letter
                    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
                    from reportlab.lib.styles import getSampleStyleSheet
                    from reportlab.lib.units import inch
                    
                    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
                    styles = getSampleStyleSheet()
                    story = []
                    
                    # Add title
                    story.append(Paragraph("Quantum Circuit Analysis Report", styles['Title']))
                    story.append(Spacer(1, 0.2*inch))
                    
                    # Add circuit diagram
                    story.append(Paragraph("Circuit Diagram:", styles['Heading2']))
                    # Save circuit as image first
                    circuit_img_path = destination / f"{base_name}_temp.png"
                    fig.savefig(circuit_img_path, format="png", dpi=150, bbox_inches="tight")
                    from reportlab.platypus import Image
                    story.append(Image(str(circuit_img_path), width=6*inch, height=4*inch))
                    story.append(Spacer(1, 0.2*inch))
                    
                    # Add analysis
                    story.append(Paragraph("Analysis:", styles['Heading2']))
                    # Split analysis text into paragraphs
                    for line in analysis_text.split('\n'):
                        if line.strip():
                            story.append(Paragraph(line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), styles['Normal']))
                        else:
                            story.append(Spacer(1, 0.1*inch))
                    
                    doc.build(story)
                    # Clean up temp image
                    circuit_img_path.unlink(missing_ok=True)
                except ImportError:
                    # Fallback: just save circuit diagram as PDF
                    fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
            else:
                # Just save circuit diagram
                fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
            exported.append(pdf_path)
        plt.close(fig)

    return exported


def _circuit_to_cirq_python(circuit: cirq.Circuit) -> str:
    """Convert Cirq circuit to Python code string."""
    lines = ["import cirq", ""]
    qubits = sorted(circuit.all_qubits())
    
    # Generate qubit definitions
    if len(qubits) <= 3:
        qubit_names = [f"q{i}" for i in range(len(qubits))]
        for i, qubit in enumerate(qubits):
            if isinstance(qubit, cirq.LineQubit):
                lines.append(f"q{i} = cirq.LineQubit({qubit.x})")
            else:
                lines.append(f"q{i} = {repr(qubit)}")
    else:
        lines.append(f"qubits = cirq.LineQubit.range({len(qubits)})")
        qubit_names = [f"qubits[{i}]" for i in range(len(qubits))]
    
    lines.append("")
    lines.append("circuit = cirq.Circuit([")
    
    # Convert operations
    for moment in circuit:
        for op in moment:
            gate = op.gate if isinstance(op, cirq.GateOperation) else None
            if gate is None:
                continue
            
            # Get qubit indices
            op_qubits = []
            for q in op.qubits:
                try:
                    idx = qubits.index(q)
                    op_qubits.append(qubit_names[idx])
                except ValueError:
                    op_qubits.append(repr(q))
            
            # Convert gate to Python
            gate_name = type(gate).__name__
            if gate_name == "H":
                lines.append(f"    cirq.H({op_qubits[0]}),")
            elif gate_name == "X":
                lines.append(f"    cirq.X({op_qubits[0]}),")
            elif gate_name == "Y":
                lines.append(f"    cirq.Y({op_qubits[0]}),")
            elif gate_name == "Z":
                lines.append(f"    cirq.Z({op_qubits[0]}),")
            elif gate_name == "CNOT" or gate_name == "CX":
                lines.append(f"    cirq.CNOT({op_qubits[0]}, {op_qubits[1]}),")
            elif gate_name == "CZ":
                lines.append(f"    cirq.CZ({op_qubits[0]}, {op_qubits[1]}),")
            elif gate_name == "SWAP":
                lines.append(f"    cirq.SWAP({op_qubits[0]}, {op_qubits[1]}),")
            elif gate_name == "ISWAP":
                lines.append(f"    cirq.ISWAP({op_qubits[0]}, {op_qubits[1]}),")
            elif gate_name == "CCX" or gate_name == "TOFFOLI":
                lines.append(f"    cirq.CCX({op_qubits[0]}, {op_qubits[1]}, {op_qubits[2]}),")
            elif gate_name == "FREDKIN" or gate_name == "CSWAP":
                lines.append(f"    cirq.FREDKIN({op_qubits[0]}, {op_qubits[1]}, {op_qubits[2]}),")
            else:
                # Generic gate
                qubit_str = ", ".join(op_qubits)
                lines.append(f"    {gate_name}().on({qubit_str}),")
    
    lines.append("])")
    lines.append("")
    lines.append("return circuit")
    return "\n".join(lines)


def _cirq_to_qasm(circuit: cirq.Circuit) -> str:
    try:
        return cirq.qasm(circuit)
    except AttributeError as exc:  # pragma: no cover - compatibility fallback
        try:
            from cirq.contrib.qasm_export import circuit_to_qasm
        except ImportError as inner_exc:
            raise RuntimeError("Cirq QASM export requires cirq>=0.12 with qasm support.") from inner_exc
        return circuit_to_qasm(circuit)
    except TypeError as exc:
        raise RuntimeError(f"Cirq circuit cannot be converted to QASM: {exc}") from exc


def export_cirq_circuit(
    circuit: cirq.Circuit, 
    destination: Path, 
    base_name: str, 
    formats: Iterable[str],
    analysis_text: Optional[str] = None
) -> Sequence[Path]:
    destination.mkdir(parents=True, exist_ok=True)
    formats = _normalize_formats(formats)
    exported: list[Path] = []

    # Cirq Python code
    if "cirq_python" in formats:
        python_path = destination / f"{base_name}_cirq.py"
        python_code = _circuit_to_cirq_python(circuit)
        python_path.write_text(python_code, encoding="utf-8")
        exported.append(python_path)

    # JSON circuit description
    if "json" in formats:
        json_path = destination / f"{base_name}.json"
        circuit_data = {
            "num_qubits": len(circuit.all_qubits()),
            "instructions": []
        }
        for moment in circuit:
            for op in moment:
                if isinstance(op, cirq.GateOperation):
                    gate_info = {
                        "name": type(op.gate).__name__,
                        "qubits": [str(q) for q in op.qubits],
                    }
                    circuit_data["instructions"].append(gate_info)
        json_path.write_text(json.dumps(circuit_data, indent=2), encoding="utf-8")
        exported.append(json_path)

    # JavaScript
    if "javascript" in formats:
        js_path = destination / f"{base_name}.js"
        circuit_data = {
            "numQubits": len(circuit.all_qubits()),
            "gates": []
        }
        for moment in circuit:
            for op in moment:
                if isinstance(op, cirq.GateOperation):
                    gate_obj = {
                        "name": type(op.gate).__name__,
                        "qubits": [str(q) for q in op.qubits]
                    }
                    circuit_data["gates"].append(gate_obj)
        js_code = f"// Quantum Circuit in JavaScript\nconst circuit = {json.dumps(circuit_data, indent=2)};\n\nexport default circuit;"
        js_path.write_text(js_code, encoding="utf-8")
        exported.append(js_path)

    # For visual formats (PNG, SVG, PDF) and QASM, convert to Qiskit first
    qasm_cache: str | None = None
    if "qasm" in formats or any(fmt in {"png", "svg", "pdf", "latex"} for fmt in formats):
        qasm_cache = _cirq_to_qasm(circuit)

    if "qasm" in formats and qasm_cache is not None:
        qasm_path = destination / f"{base_name}.qasm"
        qasm_path.write_text(qasm_cache, encoding="utf-8")
        exported.append(qasm_path)

    # Convert to Qiskit for visual formats
    if qasm_cache and any(fmt in {"png", "svg", "pdf", "latex"} for fmt in formats):
        try:
            qc = QuantumCircuit.from_qasm_str(qasm_cache)
        except AttributeError:
            from qiskit.converters import circuit_from_qasm_str
            qc = circuit_from_qasm_str(qasm_cache)
        visual_formats = [fmt for fmt in formats if fmt in {"png", "svg", "pdf", "latex"}]
        paths = export_qiskit_circuit(qc, destination, base_name, visual_formats, analysis_text)
        exported.extend(paths)

    return exported

