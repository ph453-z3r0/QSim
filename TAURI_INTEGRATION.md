# Tauri Integration Guide

This guide shows how to integrate the IndiQSim Python backend with your Tauri frontend.

## Quick Start

The `api.py` module provides direct function calls (no CLI overhead) for maximum performance.

## API Functions

### `export_circuit_api()`

Export a circuit with customizable parameters.

**Parameters:**
- `backend`: `'qiskit'` or `'cirq'`
- `source`: Path to Python file (optional)
- `code`: Inline Python code (optional)
- `callable_name`: Name of function that returns circuit (optional)
- `formats`: List of formats: `['png', 'svg', 'qasm', 'qiskit_python', 'cirq_python', 'json', 'pdf', 'latex', 'javascript']`
- `output`: Output directory (default: `"exports"`)
- `base_name`: Base filename (default: `"custom_circuit"`)
- `analysis_format`: `'text'`, `'json'`, or `'comprehensive'` (default: `'comprehensive'`)
- `histogram_bins`: Optional number of bins for histograms
- `histogram_width`: Width of histogram in characters (default: 50)

**Returns:**
```json
{
  "success": true,
  "files": ["path/to/file1.png", "path/to/file2.qasm", ...],
  "report_path": "path/to/analysis.txt",
  "report": "Full analysis text...",
  "analysis": { /* analysis dict */ },
  "supported_formats": ["png", "svg", ...]
}
```

### `analyze_circuit_api()`

Analyze a circuit without exporting.

**Parameters:** Same as `export_circuit_api()` but without `formats`, `output`, `base_name`.

**Returns:**
```json
{
  "success": true,
  "report": "Analysis text...",
  "analysis": { /* analysis dict */ }
}
```

### `get_supported_formats()`

Get list of supported export formats.

**Returns:**
```json
{
  "formats": ["png", "svg", "qasm", ...],
  "descriptions": {
    "png": "PNG circuit diagram",
    "svg": "SVG circuit diagram",
    ...
  }
}
```

## Tauri Integration (Rust)

### Option 1: Optimized Subprocess (Recommended)

```rust
// src-tauri/src/main.rs

use serde::{Deserialize, Serialize};
use std::process::Command;
use std::path::PathBuf;

#[derive(Debug, Serialize, Deserialize)]
struct ExportRequest {
    backend: String,
    source: Option<String>,
    code: Option<String>,
    callable: Option<String>,
    formats: Vec<String>,
    output: String,
    base_name: Option<String>,
    analysis_format: Option<String>,
}

#[tauri::command]
async fn export_circuit(request: ExportRequest) -> Result<serde_json::Value, String> {
    // Build Python code to call API
    let mut python_code = String::from(
        "import sys, json\n\
        sys.path.insert(0, '.')\n\
        from indiqsim_cli.api import export_circuit_api\n\n\
        result = export_circuit_api(\n"
    );
    
    python_code.push_str(&format!("    backend='{}',\n", request.backend));
    
    if let Some(ref source) = request.source {
        python_code.push_str(&format!("    source='{}',\n", source));
    }
    if let Some(ref code) = request.code {
        python_code.push_str(&format!("    code='{}',\n", code.replace('\'', "\\'")));
    }
    if let Some(ref callable) = request.callable {
        python_code.push_str(&format!("    callable_name='{}',\n", callable));
    }
    
    python_code.push_str(&format!("    formats={:?},\n", request.formats));
    python_code.push_str(&format!("    output='{}',\n", request.output));
    
    if let Some(ref base_name) = request.base_name {
        python_code.push_str(&format!("    base_name='{}',\n", base_name));
    }
    
    python_code.push_str(&format!(
        "    analysis_format='{}'\n",
        request.analysis_format.unwrap_or_else(|| "comprehensive".to_string())
    ));
    python_code.push_str(")\nprint(json.dumps(result))");
    
    let output = Command::new("python")
        .arg("-c")
        .arg(&python_code)
        .current_dir(std::env::current_dir().unwrap())
        .output()
        .map_err(|e| format!("Failed to execute: {}", e))?;
    
    if !output.status.success() {
        let error = String::from_utf8_lossy(&output.stderr);
        return Err(format!("Python error: {}", error));
    }
    
    let stdout = String::from_utf8_lossy(&output.stdout);
    serde_json::from_str(&stdout)
        .map_err(|e| format!("Failed to parse JSON: {}", e))
}

#[tauri::command]
async fn analyze_circuit(
    backend: String,
    source: Option<String>,
    code: Option<String>,
    callable: Option<String>,
    format: Option<String>,
) -> Result<serde_json::Value, String> {
    let mut python_code = String::from(
        "import sys, json\n\
        sys.path.insert(0, '.')\n\
        from indiqsim_cli.api import analyze_circuit_api\n\n\
        result = analyze_circuit_api(\n"
    );
    
    python_code.push_str(&format!("    backend='{}',\n", backend));
    
    if let Some(ref source) = source {
        python_code.push_str(&format!("    source='{}',\n", source));
    }
    if let Some(ref code) = code {
        python_code.push_str(&format!("    code='{}',\n", code.replace('\'', "\\'")));
    }
    if let Some(ref callable) = callable {
        python_code.push_str(&format!("    callable_name='{}',\n", callable));
    }
    
    python_code.push_str(&format!(
        "    format='{}'\n",
        format.unwrap_or_else(|| "comprehensive".to_string())
    ));
    python_code.push_str(")\nprint(json.dumps(result))");
    
    let output = Command::new("python")
        .arg("-c")
        .arg(&python_code)
        .current_dir(std::env::current_dir().unwrap())
        .output()
        .map_err(|e| format!("Failed: {}", e))?;
    
    let stdout = String::from_utf8_lossy(&output.stdout);
    serde_json::from_str(&stdout)
        .map_err(|e| format!("Parse error: {}", e))
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![export_circuit, analyze_circuit])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

### Frontend (TypeScript)

```typescript
// src/main.ts or your component

import { invoke } from '@tauri-apps/api/tauri';

// Export circuit
async function exportCircuit() {
  try {
    const result = await invoke('export_circuit', {
      request: {
        backend: 'qiskit',
        source: 'examples/grover.py',
        callable: 'build',
        formats: ['png', 'qasm', 'qiskit_python', 'json', 'pdf'],
        output: 'exports/qiskit',
        base_name: 'my_circuit',
        analysis_format: 'comprehensive'
      }
    });
    
    if (result.success) {
      console.log('Files exported:', result.files);
      console.log('Report saved to:', result.report_path);
      // Display report in UI
      displayReport(result.report);
    } else {
      console.error('Export failed:', result.error);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

// Analyze circuit
async function analyzeCircuit() {
  try {
    const result = await invoke('analyze_circuit', {
      backend: 'qiskit',
      source: 'examples/grover.py',
      callable: 'build',
      format: 'comprehensive'
    });
    
    if (result.success) {
      displayAnalysis(result.report);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}
```

## Export Formats

- **png**: PNG circuit diagram (300 DPI)
- **svg**: SVG circuit diagram (vector)
- **qasm**: OpenQASM 2.0 standard format
- **qiskit_python**: Qiskit Python code
- **cirq_python**: Cirq Python code
- **json**: JSON circuit description
- **pdf**: PDF report with circuit diagram and analysis
- **latex**: LaTeX code for academic papers (uses qcircuit package)
- **javascript**: JavaScript circuit representation

## Example Usage

```python
from indiqsim_cli.api import export_circuit_api

# Export with multiple formats
result = export_circuit_api(
    backend='qiskit',
    source='examples/grover.py',
    callable_name='build',
    formats=['png', 'qasm', 'qiskit_python', 'json', 'pdf'],
    output='exports/my_circuit',
    base_name='grover',
    analysis_format='comprehensive'
)

print(f"Exported {len(result['files'])} files")
print(f"Report: {result['report_path']}")
```

## Performance

- **Subprocess approach**: ~10-50ms overhead per call
- **Direct API calls**: No overhead (if using PyO3)
- **Recommended**: Use subprocess approach for simplicity and speed

## Error Handling

All API functions return a dict with:
- `success`: boolean
- `error`: error message (if failed)
- `error_type`: type of error (if failed)

Always check `success` before using results.

