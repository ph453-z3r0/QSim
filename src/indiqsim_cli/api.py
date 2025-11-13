"""Direct API for Tauri integration - no CLI overhead."""

from __future__ import annotations

from typing import Dict, Any, Optional, List
import json
from pathlib import Path

from .analysis import analyse_qiskit_circuit, analyse_cirq_circuit
from .exporters import export_qiskit_circuit, export_cirq_circuit, SUPPORTED_FORMATS
from .loader import load_circuit, CircuitLoadError
from .visualizations import create_comprehensive_report


def export_circuit_api(
    backend: str,
    source: Optional[str] = None,
    code: Optional[str] = None,
    callable_name: Optional[str] = None,
    formats: Optional[List[str]] = None,
    output: str = "exports",
    base_name: str = "custom_circuit",
    analysis_format: str = "comprehensive",
    histogram_bins: Optional[int] = None,
    histogram_width: int = 50,
) -> Dict[str, Any]:
    """
    Export circuit and return results as dict.
    
    Args:
        backend: 'qiskit' or 'cirq'
        source: Path to Python file (optional)
        code: Inline Python code (optional)
        callable_name: Name of callable that returns circuit (optional)
        formats: List of export formats. Supported: png, svg, qasm, qiskit_python, 
                 cirq_python, json, pdf, latex, javascript
        output: Output directory path
        base_name: Base name for exported files
        analysis_format: 'text', 'json', or 'comprehensive'
        histogram_bins: Number of bins for histogram (optional)
        histogram_width: Width of histogram in characters
    
    Returns:
        Dict with success, files, report_path, report, and analysis keys
    """
    if formats is None:
        formats = ["png"]
    
    try:
        # Load circuit
        circuit = load_circuit(
            backend=backend,
            source=Path(source) if source else None,
            code=code,
            stdin=False,
            callable_name=callable_name,
        )
        
        # Analyze first to get analysis text for PDF reports
        if backend == "qiskit":
            analysis = analyse_qiskit_circuit(circuit)
        else:
            analysis = analyse_cirq_circuit(circuit)
        
        # Generate report text
        if analysis_format == "comprehensive":
            report_text = create_comprehensive_report(analysis, histogram_bins, histogram_width)
        elif analysis_format == "json":
            report_text = json.dumps(analysis.to_dict(), indent=2)
        else:
            from .cli import _format_analysis_text
            report_text = _format_analysis_text(analysis, "Analysis")
        
        # Export circuit
        output_path = Path(output)
        if backend == "qiskit":
            file_paths = export_qiskit_circuit(
                circuit, output_path, base_name, formats, 
                analysis_text=report_text if "pdf" in formats else None
            )
        else:
            file_paths = export_cirq_circuit(
                circuit, output_path, base_name, formats,
                analysis_text=report_text if "pdf" in formats else None
            )
        
        # Save report
        report_ext = "json" if analysis_format == "json" else "txt"
        report_path = output_path / f"{base_name}_analysis.{report_ext}"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report_text, encoding="utf-8")
        
        return {
            "success": True,
            "files": [str(p) for p in file_paths],
            "report_path": str(report_path),
            "report": report_text,
            "analysis": analysis.to_dict(),
            "supported_formats": list(SUPPORTED_FORMATS),
        }
    except CircuitLoadError as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": "CircuitLoadError",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def analyze_circuit_api(
    backend: str,
    source: Optional[str] = None,
    code: Optional[str] = None,
    callable_name: Optional[str] = None,
    format: str = "comprehensive",
    histogram_bins: Optional[int] = None,
    histogram_width: int = 50,
) -> Dict[str, Any]:
    """
    Analyze circuit and return results as dict.
    
    Args:
        backend: 'qiskit' or 'cirq'
        source: Path to Python file (optional)
        code: Inline Python code (optional)
        callable_name: Name of callable that returns circuit (optional)
        format: 'text', 'json', or 'comprehensive'
        histogram_bins: Number of bins for histogram (optional)
        histogram_width: Width of histogram in characters
    
    Returns:
        Dict with success, report, and analysis keys
    """
    try:
        # Load circuit
        circuit = load_circuit(
            backend=backend,
            source=Path(source) if source else None,
            code=code,
            stdin=False,
            callable_name=callable_name,
        )
        
        # Analyze
        if backend == "qiskit":
            analysis = analyse_qiskit_circuit(circuit)
        else:
            analysis = analyse_cirq_circuit(circuit)
        
        # Generate report
        if format == "comprehensive":
            report_text = create_comprehensive_report(analysis, histogram_bins, histogram_width)
        elif format == "json":
            report_text = json.dumps(analysis.to_dict(), indent=2)
        else:
            from .cli import _format_analysis_text
            report_text = _format_analysis_text(analysis)
        
        return {
            "success": True,
            "report": report_text,
            "analysis": analysis.to_dict(),
        }
    except CircuitLoadError as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": "CircuitLoadError",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def get_supported_formats() -> Dict[str, Any]:
    """Return list of supported export formats."""
    return {
        "formats": list(SUPPORTED_FORMATS),
        "descriptions": {
            "png": "PNG circuit diagram",
            "svg": "SVG circuit diagram",
            "qasm": "OpenQASM 2.0 standard",
            "qiskit_python": "Qiskit Python code",
            "cirq_python": "Cirq Python code",
            "json": "JSON circuit description",
            "pdf": "PDF report with analysis",
            "latex": "LaTeX for academic papers",
            "javascript": "JavaScript circuit representation",
        }
    }


# Convenience function for direct Python calls
def quick_export(
    backend: str,
    code: str,
    formats: List[str] = None,
    output: str = "exports"
) -> Dict[str, Any]:
    """
    Quick export function for inline code.
    
    Example:
        result = quick_export('qiskit', 'from qiskit import QuantumCircuit; qc = QuantumCircuit(2); qc.h(0); qc.cx(0,1)', ['png', 'qasm'])
    """
    return export_circuit_api(
        backend=backend,
        code=code,
        formats=formats or ["png"],
        output=output,
        analysis_format="comprehensive"
    )

