# IndiQSim Python API Usage Guide

Complete guide to using the IndiQSim Python API for programmatic circuit design, analysis, and export.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Basic Usage](#basic-usage)
4. [API Reference](#api-reference)
5. [Examples](#examples)
6. [Error Handling](#error-handling)
7. [Advanced Features](#advanced-features)

## Overview

The IndiQSim API provides direct Python function calls for:
- Exporting circuits in multiple formats
- Analyzing quantum circuits
- Getting supported formats
- Quick export operations

**Advantages over CLI:**
- No subprocess overhead
- Direct function calls
- Structured return values
- Easy integration with other Python code
- Better error handling

## Installation

The API is part of the IndiQSim package. Ensure you have the project structure set up:

```python
# Add src/ to Python path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from indiqsim_cli.api import export_circuit_api, analyze_circuit_api
```

Or use the convenience launcher:
```python
# From project root
from src.indiqsim_cli.api import export_circuit_api
```

## Basic Usage

### Quick Export

```python
from indiqsim_cli.api import quick_export

result = quick_export(
    backend='qiskit',
    code='from qiskit import QuantumCircuit; qc = QuantumCircuit(2); qc.h(0); qc.cx(0,1)',
    formats=['png', 'qasm'],
    output='exports/quick'
)

if result['success']:
    print(f"Files: {result['files']}")
```

### Full Export with Analysis

```python
from indiqsim_cli.api import export_circuit_api

result = export_circuit_api(
    backend='qiskit',
    source='examples/grover.py',
    callable_name='build',
    formats=['png', 'svg', 'qasm', 'json'],
    output='exports/my_circuit',
    base_name='grover',
    analysis_format='comprehensive'
)

if result['success']:
    print(f"✓ Exported {len(result['files'])} files")
    print(f"✓ Report saved to: {result['report_path']}")
    # Access full analysis
    analysis = result['analysis']
    print(f"  Qubits: {analysis['qubits']}")
    print(f"  Depth: {analysis['depth']}")
else:
    print(f"✗ Error: {result['error']}")
```

## API Reference

### `export_circuit_api()`

Export a circuit with customizable parameters.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `backend` | `str` | Yes | - | `'qiskit'` or `'cirq'` |
| `source` | `str` | No* | `None` | Path to Python file |
| `code` | `str` | No* | `None` | Inline Python code |
| `callable_name` | `str` | No | `None` | Function name that returns circuit |
| `formats` | `List[str]` | No | `['png']` | Export formats (see below) |
| `output` | `str` | No | `'exports'` | Output directory |
| `base_name` | `str` | No | `'custom_circuit'` | Base filename |
| `analysis_format` | `str` | No | `'comprehensive'` | `'text'`, `'json'`, or `'comprehensive'` |
| `histogram_bins` | `int` | No | `None` | Number of bins for histograms |
| `histogram_width` | `int` | No | `50` | Histogram width in characters |

\* Either `source` or `code` must be provided.

#### Supported Formats

- `'png'` - PNG circuit diagram (300 DPI)
- `'svg'` - SVG vector diagram
- `'qasm'` - OpenQASM 2.0
- `'qiskit_python'` - Qiskit Python code
- `'cirq_python'` - Cirq Python code
- `'json'` - JSON circuit description
- `'pdf'` - PDF report with analysis
- `'latex'` - LaTeX (qcircuit package)
- `'javascript'` - JavaScript representation

#### Return Value

```python
{
    "success": True,
    "files": ["path/to/file1.png", "path/to/file2.qasm", ...],
    "report_path": "path/to/analysis.txt",
    "report": "Full analysis text...",
    "analysis": {
        "backend": "qiskit",
        "qubits": 2,
        "depth": 3,
        "operations": 5,
        "operations_by_type": {"h": 4, "cz": 1},
        "state_vector": [...],
        "probabilities": {...},
        "measurements": 0,
        "has_measurements": False
    },
    "supported_formats": ["png", "svg", ...]
}
```

On error:
```python
{
    "success": False,
    "error": "Error message",
    "error_type": "ExceptionType"
}
```

### `analyze_circuit_api()`

Analyze a circuit without exporting files.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `backend` | `str` | Yes | - | `'qiskit'` or `'cirq'` |
| `source` | `str` | No* | `None` | Path to Python file |
| `code` | `str` | No* | `None` | Inline Python code |
| `callable_name` | `str` | No | `None` | Function name |
| `format` | `str` | No | `'comprehensive'` | Analysis format |
| `histogram_bins` | `int` | No | `None` | Histogram bins |
| `histogram_width` | `int` | No | `50` | Histogram width |

\* Either `source` or `code` must be provided.

#### Return Value

```python
{
    "success": True,
    "report": "Analysis text...",
    "analysis": { /* analysis dict */ }
}
```

### `get_supported_formats()`

Get list of supported export formats.

#### Return Value

```python
{
    "formats": ["png", "svg", "qasm", ...],
    "descriptions": {
        "png": "PNG circuit diagram",
        "svg": "SVG circuit diagram",
        ...
    }
}
```

### `quick_export()`

Convenience function for quick exports with inline code.

#### Parameters

- `backend`: `'qiskit'` or `'cirq'`
- `code`: Inline Python code string
- `formats`: List of formats (default: `['png']`)
- `output`: Output directory (default: `'exports'`)

## Examples

### Example 1: Export from File

```python
from indiqsim_cli.api import export_circuit_api

result = export_circuit_api(
    backend='qiskit',
    source='examples/grover.py',
    callable_name='build',
    formats=['png', 'qasm', 'qiskit_python'],
    output='exports/grover',
    analysis_format='comprehensive'
)

if result['success']:
    for file_path in result['files']:
        print(f"Created: {file_path}")
    print(f"\nAnalysis report: {result['report_path']}")
```

### Example 2: Export from Inline Code

```python
from indiqsim_cli.api import export_circuit_api

code = """
from qiskit import QuantumCircuit

def build_bell_state():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return qc
"""

result = export_circuit_api(
    backend='qiskit',
    code=code,
    callable_name='build_bell_state',
    formats=['png', 'svg', 'json'],
    output='exports/bell',
    base_name='bell_state'
)
```

### Example 3: Analyze Only

```python
from indiqsim_cli.api import analyze_circuit_api

result = analyze_circuit_api(
    backend='qiskit',
    source='examples/grover.py',
    callable_name='build',
    format='comprehensive'
)

if result['success']:
    # Save report to custom location
    with open('my_analysis.txt', 'w') as f:
        f.write(result['report'])
    
    # Access structured data
    analysis = result['analysis']
    print(f"Qubits: {analysis['qubits']}")
    print(f"Depth: {analysis['depth']}")
    print(f"Probabilities: {analysis['probabilities']}")
```

### Example 4: Multiple Formats

```python
from indiqsim_cli.api import export_circuit_api

# Export in all formats
all_formats = [
    'png', 'svg',           # Visual diagrams
    'qasm',                  # OpenQASM
    'qiskit_python',         # Qiskit code
    'cirq_python',           # Cirq code
    'json',                  # JSON description
    'pdf',                   # PDF report
    'latex',                 # LaTeX
    'javascript'             # JavaScript
]

result = export_circuit_api(
    backend='qiskit',
    source='examples/grover.py',
    callable_name='build',
    formats=all_formats,
    output='exports/all_formats',
    analysis_format='comprehensive'
)

print(f"Exported {len(result['files'])} files")
```

### Example 5: Custom Analysis Parameters

```python
from indiqsim_cli.api import export_circuit_api

result = export_circuit_api(
    backend='qiskit',
    source='examples/grover.py',
    callable_name='build',
    formats=['png'],
    output='exports/custom',
    analysis_format='comprehensive',
    histogram_bins=30,      # Custom histogram bins
    histogram_width=60      # Wider histogram
)
```

### Example 6: Error Handling

```python
from indiqsim_cli.api import export_circuit_api

result = export_circuit_api(
    backend='qiskit',
    source='nonexistent.py',
    callable_name='build',
    formats=['png']
)

if not result['success']:
    error_type = result['error_type']
    error_msg = result['error']
    
    if error_type == 'CircuitLoadError':
        print(f"Failed to load circuit: {error_msg}")
    elif error_type == 'FileNotFoundError':
        print(f"File not found: {error_msg}")
    else:
        print(f"Unexpected error ({error_type}): {error_msg}")
else:
    print("Export successful!")
```

### Example 7: Batch Processing

```python
from indiqsim_cli.api import export_circuit_api

circuits = [
    {'source': 'examples/grover.py', 'callable': 'build', 'name': 'grover'},
    {'source': 'examples/bell.py', 'callable': 'build', 'name': 'bell'},
    {'source': 'examples/qft.py', 'callable': 'build', 'name': 'qft'},
]

for circuit in circuits:
    result = export_circuit_api(
        backend='qiskit',
        source=circuit['source'],
        callable_name=circuit['callable'],
        formats=['png', 'qasm', 'json'],
        output=f"exports/{circuit['name']}",
        base_name=circuit['name']
    )
    
    if result['success']:
        print(f"✓ {circuit['name']}: {len(result['files'])} files")
    else:
        print(f"✗ {circuit['name']}: {result['error']}")
```

## Error Handling

Always check the `success` field before using results:

```python
result = export_circuit_api(...)

if result['success']:
    # Use result['files'], result['report'], etc.
    pass
else:
    # Handle error
    print(f"Error: {result['error']}")
    print(f"Type: {result['error_type']}")
```

### Common Error Types

- `CircuitLoadError`: Failed to load/create circuit
- `FileNotFoundError`: Source file not found
- `ValueError`: Invalid parameter value
- `ImportError`: Missing dependencies
- `RuntimeError`: Export/analysis failure

## Advanced Features

### Custom Histogram Configuration

```python
result = export_circuit_api(
    ...,
    histogram_bins=50,      # More bins for finer detail
    histogram_width=80      # Wider display
)
```

### JSON Analysis Format

```python
result = export_circuit_api(
    ...,
    analysis_format='json'  # Get structured JSON instead of text
)

# Parse JSON report
import json
report_data = json.loads(result['report'])
```

### Accessing State Vector

```python
result = export_circuit_api(...)

if result['success']:
    analysis = result['analysis']
    state_vector = analysis.get('state_vector')
    
    if state_vector:
        for i, amplitude in enumerate(state_vector):
            if abs(amplitude) > 1e-10:
                print(f"|{i:02b}>: {amplitude}")
```

### Accessing Probabilities

```python
result = export_circuit_api(...)

if result['success']:
    analysis = result['analysis']
    probabilities = analysis.get('probabilities', {})
    
    # Sort by probability
    sorted_probs = sorted(
        probabilities.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    for basis_state, prob in sorted_probs:
        print(f"|{basis_state}>: {prob:.4f} ({prob*100:.2f}%)")
```

## Integration Tips

### With Tauri

See `TAURI_INTEGRATION.md` for complete Tauri integration guide.

### With Flask/FastAPI

```python
from flask import Flask, request, jsonify
from indiqsim_cli.api import export_circuit_api

app = Flask(__name__)

@app.route('/api/export', methods=['POST'])
def export():
    data = request.json
    result = export_circuit_api(**data)
    return jsonify(result)
```

### With Jupyter Notebooks

```python
from indiqsim_cli.api import export_circuit_api, analyze_circuit_api

# In notebook
result = export_circuit_api(
    backend='qiskit',
    code='from qiskit import QuantumCircuit; qc = QuantumCircuit(2); qc.h(0); qc.cx(0,1); CIRCUIT=qc',
    formats=['png', 'svg']
)

# Display results
from IPython.display import Image, display
for file in result['files']:
    if file.endswith('.png'):
        display(Image(file))
```

## Performance Tips

1. **Use API instead of CLI** for programmatic access (faster)
2. **Batch operations** when processing multiple circuits
3. **Cache analysis results** if reusing the same circuit
4. **Use appropriate formats** - don't export unnecessary formats
5. **Set histogram parameters** only if needed (uses defaults otherwise)

## See Also

- [CLI Usage Guide](CLI_USAGE.md) - Command-line interface
- [Tauri Integration](TAURI_INTEGRATION.md) - Desktop app integration
- [README.md](README.md) - Project overview

