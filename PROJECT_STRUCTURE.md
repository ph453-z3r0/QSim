# Project Structure

```
IndiQSim/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI workflow
├── docs/                       # Documentation files (Word docs)
│   ├── BB84 Quantum Key Distribution.docx
│   ├── Commercial Aspect.docx
│   ├── Full List of Common Quantum Gates.docx
│   ├── IndiQSim.docx
│   ├── Minimum system requirement.docx
│   └── Truth_Table.docx
├── examples/                   # Example circuit files
│   └── grover.py              # Example Grover's algorithm circuit
├── src/
│   └── indiqsim_cli/          # Main package
│       ├── __init__.py
│       ├── __main__.py         # CLI entry point
│       ├── api.py              # Python API for integration
│       ├── cli.py              # Command-line interface
│       ├── loader.py           # Circuit loading from code
│       ├── exporters.py        # Export format handlers
│       ├── analysis.py         # Circuit analysis engine
│       ├── visualizations.py   # Text-based visualizations
│       ├── gate_library.py     # Quantum gate definitions
│       └── algorithm_library.py # Pre-built algorithms
├── .gitignore                  # Git ignore rules
├── app.py                      # Convenience launcher
├── requirements.txt            # Python dependencies
├── LICENSE                     # MIT License
├── README.md                   # Main documentation
├── QUICK_START.md             # Quick start guide
├── CLI_USAGE.md               # CLI usage guide
├── API_USAGE.md               # Python API guide
├── TAURI_INTEGRATION.md       # Tauri integration guide
├── CONTRIBUTING.md            # Contribution guidelines
├── CHANGELOG.md               # Version history
└── PROJECT_STRUCTURE.md       # This file
```

## Directory Descriptions

### `src/indiqsim_cli/`
Main package containing all core functionality.

- **api.py**: Python API functions for programmatic access
- **cli.py**: Command-line interface implementation
- **loader.py**: Loads circuits from Python code (file, inline, or stdin)
- **exporters.py**: Handles all export formats
- **analysis.py**: Circuit analysis and metrics calculation
- **visualizations.py**: Text-based visualization generators
- **gate_library.py**: Quantum gate definitions and builders
- **algorithm_library.py**: Pre-built quantum algorithms

### `examples/`
Example circuit files demonstrating usage.

### `docs/`
Original documentation files (Word documents).

### Root Files
- **app.py**: Convenience launcher that handles Python path
- **requirements.txt**: Python package dependencies
- **README.md**: Main project documentation
- **CLI_USAGE.md**: Complete CLI guide
- **API_USAGE.md**: Complete API guide
- **TAURI_INTEGRATION.md**: Tauri desktop app integration
- **QUICK_START.md**: Quick reference guide
- **CONTRIBUTING.md**: Contribution guidelines
- **CHANGELOG.md**: Version history
- **LICENSE**: MIT License

## File Naming Conventions

- Python modules: `snake_case.py`
- Documentation: `UPPER_CASE.md`
- Example files: `lowercase.py`
- Config files: `lowercase.ext`

## Excluded from Git

The following are excluded via `.gitignore`:
- `__pycache__/` - Python bytecode
- `exports/` - User-generated export files
- `*.pyc` - Compiled Python files
- `.venv/` - Virtual environments
- `*.docx` - Word documents (moved to docs/)

