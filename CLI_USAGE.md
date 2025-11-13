# IndiQSim CLI Usage Guide

Complete guide to using the IndiQSim command-line interface for quantum circuit design, analysis, and export.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Basic Commands](#basic-commands)
4. [Command Reference](#command-reference)
5. [Export Formats](#export-formats)
6. [Examples](#examples)
7. [Tips & Tricks](#tips--tricks)
8. [Troubleshooting](#troubleshooting)

## Overview

The IndiQSim CLI provides a command-line interface for:
- Exporting circuits in multiple formats
- Analyzing quantum circuits
- Generating comprehensive analysis reports
- Working with both Qiskit and Cirq backends

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Install dependencies**:
   ```bash
   pip install qiskit cirq matplotlib
   ```

2. **Optional (for PDF reports)**:
   ```bash
   pip install reportlab
   ```

3. **Verify installation**:
   ```bash
   python app.py --help
   ```

## Basic Commands

### Get Help

```bash
# General help
python app.py --help

# Command-specific help
python app.py export --help
python app.py analyze --help
```

### Export Command

Export circuits to various formats with optional analysis.

```bash
python app.py export --backend <qiskit|cirq> \
    --source <file> OR --code <code> OR --stdin \
    [--callable <name>] \
    --format <format1> [--format <format2> ...] \
    [--output <directory>] \
    [--analysis-format <text|json|comprehensive>]
```

### Analyze Command

Analyze circuits without exporting files.

```bash
python app.py analyze --backend <qiskit|cirq> \
    --source <file> OR --code <code> OR --stdin \
    [--callable <name>] \
    [--format <text|json|comprehensive>] \
    [--output <directory>]
```

## Command Reference

### Global Options

| Option | Description |
|--------|-------------|
| `--help` | Show help message |

### Export Command Options

| Option | Required | Description |
|--------|----------|-------------|
| `--backend` | Yes | Backend: `qiskit` or `cirq` |
| `--source` | Yes* | Path to Python file |
| `--code` | Yes* | Inline Python code |
| `--stdin` | Yes* | Read from standard input |
| `--callable` | No | Function name that returns circuit |
| `--format` | Yes | Export format (can specify multiple) |
| `--output` | No | Output directory (default: `exports/`) |
| `--analysis-format` | No | Analysis format: `text`, `json`, or `comprehensive` (default: `text`) |

\* Exactly one of `--source`, `--code`, or `--stdin` must be provided.

### Analyze Command Options

| Option | Required | Description |
|--------|----------|-------------|
| `--backend` | Yes | Backend: `qiskit` or `cirq` |
| `--source` | Yes* | Path to Python file |
| `--code` | Yes* | Inline Python code |
| `--stdin` | Yes* | Read from standard input |
| `--callable` | No | Function name that returns circuit |
| `--format` | No | Analysis format: `text`, `json`, or `comprehensive` (default: `text`) |
| `--output` | No | Save report to file in this directory |

\* Exactly one of `--source`, `--code`, or `--stdin` must be provided.

## Export Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| `png` | `.png` | PNG circuit diagram (300 DPI) |
| `svg` | `.svg` | SVG vector diagram |
| `qasm` | `.qasm` | OpenQASM 2.0 standard |
| `qiskit_python` | `_qiskit.py` | Qiskit Python code |
| `cirq_python` | `_cirq.py` | Cirq Python code |
| `json` | `.json` | JSON circuit description |
| `pdf` | `.pdf` | PDF report with analysis |
| `latex` | `.tex` | LaTeX (qcircuit package) |
| `javascript` | `.js` | JavaScript representation |

## Examples

### Example 1: Basic Export from File

Create a circuit file `examples/bell.py`:
```python
from qiskit import QuantumCircuit

def build():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return qc
```

Export:
```bash
python app.py export --backend qiskit \
    --source examples/bell.py \
    --callable build \
    --format png \
    --format qasm \
    --output exports/bell
```

### Example 2: Export with Comprehensive Analysis

```bash
python app.py export --backend qiskit \
    --source examples/grover.py \
    --callable build \
    --format png \
    --format qasm \
    --format json \
    --output exports/grover \
    --analysis-format comprehensive
```

This creates:
- `exports/grover/custom_circuit.png`
- `exports/grover/custom_circuit.qasm`
- `exports/grover/custom_circuit.json`
- `exports/grover/custom_circuit_analysis.txt` (comprehensive report)

### Example 3: Inline Code Export

```bash
python app.py export --backend qiskit \
    --code "from qiskit import QuantumCircuit; qc = QuantumCircuit(2); qc.h(0); qc.cx(0,1); CIRCUIT=qc" \
    --format png \
    --format svg
```

### Example 4: Multiple Formats

```bash
python app.py export --backend qiskit \
    --source examples/grover.py \
    --callable build \
    --format png \
    --format svg \
    --format qasm \
    --format qiskit_python \
    --format json \
    --format pdf \
    --format latex \
    --format javascript \
    --output exports/all_formats
```

### Example 5: Analyze Only (No Export)

```bash
python app.py analyze --backend qiskit \
    --source examples/grover.py \
    --callable build \
    --format comprehensive
```

### Example 6: Analyze and Save Report

```bash
python app.py analyze --backend qiskit \
    --source examples/grover.py \
    --callable build \
    --format comprehensive \
    --output exports/analysis
```

### Example 7: Using STDIN

```bash
cat examples/grover.py | python app.py export \
    --backend qiskit \
    --stdin \
    --callable build \
    --format png
```

Or with PowerShell:
```powershell
Get-Content examples/grover.py | python app.py export --backend qiskit --stdin --callable build --format png
```

### Example 8: Cirq Backend

```bash
python app.py export --backend cirq \
    --code "import cirq; q0,q1=cirq.LineQubit.range(2); CIRCUIT=cirq.Circuit(cirq.H(q0), cirq.CNOT(q0,q1))" \
    --format png \
    --format cirq_python \
    --output exports/cirq_circuit
```

### Example 9: JSON Analysis Output

```bash
python app.py analyze --backend qiskit \
    --source examples/grover.py \
    --callable build \
    --format json
```

Outputs structured JSON:
```json
{
  "backend": "qiskit",
  "qubits": 2,
  "depth": 3,
  "operations": 5,
  "operations_by_type": {
    "h": 4,
    "cz": 1
  },
  "state_vector": [...],
  "probabilities": {...},
  ...
}
```

### Example 10: Export with Custom Output Name

The CLI uses `custom_circuit` as the base name. To customize, you'll need to use the Python API (see `API_USAGE.md`).

## Tips & Tricks

### 1. PowerShell Line Continuation

In PowerShell, use backticks for line continuation:

```powershell
python app.py export --backend qiskit `
    --source examples/grover.py `
    --callable build `
    --format png `
    --format qasm
```

Or put everything on one line (recommended).

### 2. Batch Processing

Create a script `batch_export.sh`:
```bash
#!/bin/bash
for file in examples/*.py; do
    python app.py export --backend qiskit \
        --source "$file" \
        --callable build \
        --format png \
        --format qasm \
        --output "exports/$(basename $file .py)"
done
```

### 3. Redirect Output

Save analysis to file:
```bash
python app.py analyze --backend qiskit \
    --source examples/grover.py \
    --callable build \
    --format comprehensive > analysis.txt
```

### 4. Combine with Other Tools

Pipe to other commands:
```bash
python app.py analyze --backend qiskit \
    --source examples/grover.py \
    --callable build \
    --format json | jq '.qubits, .depth'
```

### 5. Environment Variables

Set matplotlib backend for headless servers:
```bash
# Linux/macOS
export MPLBACKEND=Agg
python app.py export ...

# Windows PowerShell
$env:MPLBACKEND="Agg"
python app.py export ...
```

## Output Files

### Export Command Output

Files are saved to the specified output directory (default: `exports/`):

- `custom_circuit.png` - PNG diagram
- `custom_circuit.svg` - SVG diagram
- `custom_circuit.qasm` - OpenQASM file
- `custom_circuit_qiskit.py` - Qiskit Python code
- `custom_circuit_cirq.py` - Cirq Python code
- `custom_circuit.json` - JSON description
- `custom_circuit.pdf` - PDF report
- `custom_circuit.tex` - LaTeX file
- `custom_circuit.js` - JavaScript file
- `custom_circuit_analysis.txt` - Analysis report

### Analysis Report Structure

The comprehensive analysis report includes:

**Tab 1: Results**
- Probability histograms
- Measurement outcomes

**Tab 2: State**
- State vector tables
- Bloch sphere coordinates
- Phase diagrams
- Amplitude distributions

**Tab 3: Analysis**
- Circuit metrics
- Entanglement heatmaps
- Performance indicators

## Troubleshooting

### Common Issues

**1. "Missing package errors"**
```bash
pip install qiskit cirq matplotlib
```

**2. "Matplotlib backend issues" (headless servers)**
```bash
# Windows PowerShell
$env:MPLBACKEND="Agg"

# Linux/macOS
export MPLBACKEND=Agg
```

**3. "File not found"**
- Use absolute paths or paths relative to current directory
- Check file exists: `ls examples/grover.py`

**4. "CircuitLoadError"**
- Ensure your code creates a `QuantumCircuit` or `cirq.Circuit`
- Use `--callable` if circuit is returned by a function
- Or set `CIRCUIT` variable in your code

**5. "Unsupported format"**
- Check format name spelling
- Use `--help` to see supported formats
- Format names are case-insensitive

**6. "PDF export fails"**
- Install reportlab: `pip install reportlab`
- PDF export requires reportlab for analysis reports

**7. "Import errors"**
- Ensure you're running from project root
- Use `python app.py` not `python -m indiqsim_cli` directly
- Check Python path includes `src/`

### Debug Mode

For more verbose output, check the Python traceback:
```bash
python app.py export ... 2>&1 | tee error.log
```

### Verify Installation

```bash
# Test import
python -c "from src.indiqsim_cli.api import get_supported_formats; print(get_supported_formats())"

# Test CLI
python app.py --help
```

## Command-Line Shortcuts

### Aliases (Optional)

Create aliases for faster access:

**Linux/macOS** (`~/.bashrc` or `~/.zshrc`):
```bash
alias indiqsim='python /path/to/Sim/app.py'
```

**Windows PowerShell** (`$PROFILE`):
```powershell
function indiqsim { python E:\Sim\app.py $args }
```

Then use:
```bash
indiqsim export --backend qiskit --source examples/grover.py --callable build --format png
```

## See Also

- [API Usage Guide](API_USAGE.md) - Python API for programmatic access
- [Tauri Integration](TAURI_INTEGRATION.md) - Desktop app integration
- [README.md](README.md) - Project overview

## Quick Reference

```bash
# Export with analysis
python app.py export --backend qiskit --source file.py --callable build --format png --analysis-format comprehensive

# Analyze only
python app.py analyze --backend qiskit --source file.py --callable build --format comprehensive

# Inline code
python app.py export --backend qiskit --code "code here" --format png

# Multiple formats
python app.py export --backend qiskit --source file.py --callable build --format png --format qasm --format json
```

---

**Happy circuit designing!** 🚀

