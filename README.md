# IndiQSim - Quantum Circuit Design & Analysis Tool

A comprehensive, offline-first tool for designing, analyzing, and exporting quantum circuits using **Qiskit** and **Cirq**. IndiQSim provides both a command-line interface and a Python API for seamless integration with desktop applications (like Tauri) and other Python projects.

## Features

### 🎯 Core Capabilities
- **Multi-Backend Support**: Works with both Qiskit and Cirq
- **Comprehensive Analysis**: State vectors, probabilities, entanglement metrics, and more
- **Multiple Export Formats**: 9 different export formats for various use cases
- **Rich Visualizations**: Probability histograms, phase diagrams, entanglement heatmaps
- **Tabbed Analysis Reports**: Organized Results, State, and Analysis sections

### 📊 Analysis Features
- **State Vector Analysis**: Full quantum state representation with complex amplitudes
- **Probability Distributions**: Measurement probabilities with histograms
- **Entanglement Metrics**: Von Neumann entropy, concurrence, correlation heatmaps
- **Bloch Sphere Representation**: 3D coordinates for single qubits
- **Phase Diagrams**: Visual phase analysis
- **Amplitude Distribution**: Statistical analysis of state amplitudes
- **Performance Indicators**: Operations per qubit, depth analysis, and more

### 📤 Export Formats
1. **PNG** - High-resolution circuit diagrams (300 DPI)
2. **SVG** - Vector circuit diagrams
3. **OpenQASM** - Universal quantum assembly language
4. **Qiskit Python** - Executable Qiskit code
5. **Cirq Python** - Executable Cirq code
6. **JSON** - Structured circuit descriptions
7. **PDF** - Professional reports with analysis
8. **LaTeX** - Academic paper format (qcircuit package)
9. **JavaScript** - Web-compatible circuit representation

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Basic Installation

1. **Clone or download the repository**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install required packages**:
   ```bash
   pip install qiskit cirq matplotlib
   ```

4. **Optional dependencies** (for PDF reports):
   ```bash
   pip install reportlab
   ```

## Quick Start

### Using the CLI

```bash
# Export a circuit with analysis
python app.py export --backend qiskit \
    --source examples/grover.py \
    --callable build \
    --format png --format qasm \
    --output exports/qiskit \
    --analysis-format comprehensive
```

### Using the Python API

```python
from indiqsim_cli.api import export_circuit_api

result = export_circuit_api(
    backend='qiskit',
    source='examples/grover.py',
    callable_name='build',
    formats=['png', 'qasm', 'qiskit_python'],
    output='exports/my_circuit',
    analysis_format='comprehensive'
)

if result['success']:
    print(f"Exported {len(result['files'])} files")
    print(f"Report: {result['report_path']}")
```

## Documentation

- **[CLI Usage Guide](CLI_USAGE.md)** - Complete guide for command-line usage
- **[API Usage Guide](API_USAGE.md)** - Python API documentation and examples
- **[Tauri Integration](TAURI_INTEGRATION.md)** - Integration guide for Tauri applications

## Project Structure

```
IndiQSim/
├── src/
│   └── indiqsim_cli/
│       ├── __init__.py
│       ├── __main__.py          # CLI entry point
│       ├── api.py                # Python API for integration
│       ├── cli.py                # Command-line interface
│       ├── loader.py             # Circuit loading from code
│       ├── exporters.py          # Export format handlers
│       ├── analysis.py           # Circuit analysis engine
│       ├── visualizations.py     # Text-based visualizations
│       ├── gate_library.py       # Quantum gate definitions
│       └── algorithm_library.py  # Pre-built algorithms
├── examples/                     # Example circuit files
├── exports/                      # Default export directory
├── app.py                        # Convenience launcher
├── README.md                     # This file
├── CLI_USAGE.md                  # CLI documentation
├── API_USAGE.md                  # API documentation
└── TAURI_INTEGRATION.md          # Tauri integration guide
```

## Supported Backends

### Qiskit
- Full support for all Qiskit circuit operations
- State vector simulation
- Comprehensive gate library

### Cirq
- Full support for Cirq circuits
- Automatic conversion to Qiskit for visualization
- Native Cirq Python code export

## Analysis Report Structure

The comprehensive analysis report includes three main sections:

### Tab 1: Results
- Measurement outcomes and probabilities
- Probability histograms with configurable binning
- Sorted probability distributions

### Tab 2: State
- Full quantum state representation
- State vector tables (sortable columns)
- Bloch sphere coordinates (3D)
- Phase diagrams
- Amplitude distribution plots

### Tab 3: Analysis
- Circuit metrics (qubits, depth, operations)
- Operations by type
- Entanglement heatmaps
- Entanglement metrics (von Neumann entropy, concurrence)
- Performance indicators

## Examples

### Example 1: Basic Circuit Export

```python
# examples/bell_state.py
from qiskit import QuantumCircuit

def build():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return qc
```

```bash
python app.py export --backend qiskit \
    --source examples/bell_state.py \
    --callable build \
    --format png --format qasm
```

### Example 2: Inline Code Analysis

```bash
python app.py analyze --backend qiskit \
    --code "from qiskit import QuantumCircuit; qc = QuantumCircuit(2); qc.h(0); qc.cx(0,1); CIRCUIT=qc" \
    --format comprehensive
```

### Example 3: Multiple Export Formats

```python
from indiqsim_cli.api import export_circuit_api

result = export_circuit_api(
    backend='qiskit',
    source='examples/grover.py',
    callable_name='build',
    formats=['png', 'svg', 'qasm', 'qiskit_python', 'json', 'pdf', 'latex', 'javascript'],
    output='exports/all_formats',
    analysis_format='comprehensive'
)
```

## Performance

- **CLI Mode**: ~50-100ms per operation (includes subprocess overhead)
- **API Mode**: ~10-50ms per operation (direct function calls)
- **Recommended**: Use API mode for integration with desktop applications

## Troubleshooting

### Common Issues

**Missing package errors**
```bash
pip install qiskit cirq matplotlib
```

**Matplotlib backend issues (headless servers)**
```bash
# Windows PowerShell
$env:MPLBACKEND="Agg"

# Linux/macOS
export MPLBACKEND=Agg
```

**Cirq QASM export failures**
- Ensure Cirq ≥ 1.0
- Older versions may need: `pip install cirq[contrib]`

**PDF export requires reportlab**
```bash
pip install reportlab
```

**Import errors**
- Ensure you're running from the project root
- Use `python app.py` instead of direct module import
- Check that `src/` is in Python path

## Contributing

This is a project for quantum circuit design and analysis. Contributions are welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Qiskit](https://qiskit.org/)
- Built with [Cirq](https://quantumai.google/cirq)
- Visualization with [Matplotlib](https://matplotlib.org/)

## Support

For issues, questions, or contributions, please refer to the documentation files:
- CLI usage: See `CLI_USAGE.md`
- API usage: See `API_USAGE.md`
- Tauri integration: See `TAURI_INTEGRATION.md`

---

**Enjoy exploring quantum circuits with IndiQSim!** 🚀
