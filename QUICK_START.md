# IndiQSim Quick Start Guide

Get started with IndiQSim in 5 minutes!

## Installation

```bash
# Install dependencies
pip install qiskit cirq matplotlib

# Optional: For PDF reports
pip install reportlab
```

## Quick Examples

### 1. Export a Circuit (CLI)

```bash
python app.py export --backend qiskit \
    --source examples/grover.py \
    --callable build \
    --format png \
    --format qasm \
    --analysis-format comprehensive
```

### 2. Export a Circuit (Python API)

```python
from src.indiqsim_cli.api import export_circuit_api

result = export_circuit_api(
    backend='qiskit',
    source='examples/grover.py',
    callable_name='build',
    formats=['png', 'qasm'],
    analysis_format='comprehensive'
)

print(f"Files: {result['files']}")
```

### 3. Analyze Only

```bash
python app.py analyze --backend qiskit \
    --source examples/grover.py \
    --callable build \
    --format comprehensive
```

### 4. Inline Code

```bash
python app.py export --backend qiskit \
    --code "from qiskit import QuantumCircuit; qc = QuantumCircuit(2); qc.h(0); qc.cx(0,1); CIRCUIT=qc" \
    --format png
```

## Supported Formats

- `png` - Circuit diagrams
- `svg` - Vector diagrams
- `qasm` - OpenQASM
- `qiskit_python` - Qiskit code
- `cirq_python` - Cirq code
- `json` - JSON descriptions
- `pdf` - PDF reports
- `latex` - LaTeX format
- `javascript` - JavaScript

## Documentation

- **[README.md](README.md)** - Project overview
- **[CLI_USAGE.md](CLI_USAGE.md)** - Command-line guide
- **[API_USAGE.md](API_USAGE.md)** - Python API guide
- **[TAURI_INTEGRATION.md](TAURI_INTEGRATION.md)** - Tauri integration

## Need Help?

Check the full documentation files for:
- Detailed examples
- Error troubleshooting
- Advanced features
- Integration guides

---

**Ready to explore quantum circuits!** 🚀

