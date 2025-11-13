"""Text-based visualizations for quantum circuit analysis."""

from __future__ import annotations

from typing import List, Dict, Tuple, Optional
import numpy as np
import math


def create_probability_histogram(probabilities: Dict[str, float], width: int = 50, bins: Optional[int] = None) -> str:
    """Create an ASCII histogram of probabilities."""
    if not probabilities:
        return "No probabilities available."
    
    lines = ["Probability Histogram:"]
    lines.append("=" * (width + 20))
    
    # Sort by probability descending
    sorted_probs = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
    
    max_prob = max(probabilities.values()) if probabilities else 1.0
    
    for basis_state, prob in sorted_probs:
        bar_length = int((prob / max_prob) * width) if max_prob > 0 else 0
        bar = "█" * bar_length
        percentage = prob * 100
        lines.append(f"|{basis_state}>: {bar:<{width}} {percentage:6.2f}%")
    
    lines.append("=" * (width + 20))
    return "\n".join(lines)


def create_state_vector_table(state_vector: List[complex], num_qubits: int, sort_by: str = "amplitude") -> str:
    """Create a formatted table of state vector with sortable-like structure."""
    if not state_vector:
        return "No state vector available."
    
    lines = ["State Vector Table (sortable-like structure):"]
    lines.append("=" * 90)
    lines.append(f"{'Basis State':<15} {'Real':<15} {'Imaginary':<15} {'Amplitude':<15} {'Phase (deg)':<15}")
    lines.append("-" * 90)
    
    # Prepare data
    data = []
    for i, amplitude in enumerate(state_vector):
        if abs(amplitude) > 1e-10:
            basis_state = format(i, f"0{num_qubits}b")
            real = amplitude.real
            imag = amplitude.imag
            amp = abs(amplitude)
            phase = math.degrees(math.atan2(imag, real)) if amp > 1e-10 else 0.0
            data.append((basis_state, real, imag, amp, phase))
    
    # Sort based on parameter
    if sort_by == "amplitude":
        data.sort(key=lambda x: x[3], reverse=True)
    elif sort_by == "real":
        data.sort(key=lambda x: x[1], reverse=True)
    elif sort_by == "imaginary":
        data.sort(key=lambda x: x[2], reverse=True)
    elif sort_by == "phase":
        data.sort(key=lambda x: x[4], reverse=True)
    else:  # basis_state
        data.sort(key=lambda x: x[0])
    
    for basis_state, real, imag, amp, phase in data:
        lines.append(f"|{basis_state}>:     {real:>14.6f} {imag:>14.6f} {amp:>14.6f} {phase:>14.2f}")
    
    lines.append("=" * 90)
    lines.append(f"Note: Table sorted by {sort_by}. Total states: {len(data)}")
    return "\n".join(lines)


def create_bloch_sphere_representation(state_vector: List[complex], num_qubits: int) -> str:
    """Create text representation of Bloch sphere coordinates for single qubits."""
    if not state_vector or num_qubits == 0:
        return "No state vector available for Bloch sphere representation."
    
    lines = ["Bloch Sphere Representation (3D coordinates):"]
    lines.append("=" * 80)
    
    if num_qubits == 1:
        # Single qubit: direct Bloch sphere
        if len(state_vector) >= 2:
            alpha = state_vector[0]
            beta = state_vector[1] if len(state_vector) > 1 else 0
            
            # Convert to Bloch sphere coordinates
            # |ψ⟩ = α|0⟩ + β|1⟩
            # x = 2*Re(α*β*)
            # y = 2*Im(α*β*)
            # z = |α|² - |β|²
            alpha_conj = np.conj(alpha)
            x = 2 * (alpha * beta.conjugate()).real
            y = 2 * (alpha * beta.conjugate()).imag
            z = abs(alpha) ** 2 - abs(beta) ** 2
            
            lines.append(f"Qubit 0:")
            lines.append(f"  X coordinate: {x:8.6f}")
            lines.append(f"  Y coordinate: {y:8.6f}")
            lines.append(f"  Z coordinate: {z:8.6f}")
            lines.append(f"  Radius: {math.sqrt(x**2 + y**2 + z**2):8.6f}")
            
            # Text visualization
            lines.append("")
            lines.append("  2D Projection (top view):")
            lines.append("      Y")
            lines.append("      |")
            lines.append("      |")
            # Simple ASCII representation
            scale = 20
            x_pos = int(x * scale) + 40
            y_pos = int(y * scale) + 20
            x_pos = max(0, min(80, x_pos))
            y_pos = max(0, min(40, y_pos))
            
            for i in range(21):
                line = f"  {i*4-40:4d} |"
                if abs(i*4-40 - y*scale) < 2:
                    line += " " * (x_pos - 5) + "●"
                lines.append(line)
            lines.append("      " + "-" * 80)
            lines.append("      " + " " * 35 + "X")
    else:
        # Multi-qubit: show reduced density matrices for each qubit
        lines.append("Multi-qubit system - Reduced density matrix for each qubit:")
        lines.append("")
        
        # Convert state vector to density matrix
        state_array = np.array(state_vector)
        density_matrix = np.outer(state_array, np.conj(state_array))
        
        for qubit_idx in range(num_qubits):
            # Trace out other qubits to get reduced density matrix
            # For simplicity, show partial trace approximation
            lines.append(f"Qubit {qubit_idx} (approximate):")
            lines.append("  Note: Full reduced density matrix calculation requires tensor operations")
            lines.append("  State vector contribution visible in full state table above")
    
    lines.append("=" * 80)
    return "\n".join(lines)


def calculate_entanglement_metrics(state_vector: List[complex], num_qubits: int) -> Dict[str, float]:
    """Calculate entanglement metrics (simplified)."""
    if not state_vector or num_qubits < 2:
        return {}
    
    metrics = {}
    
    # Calculate von Neumann entropy (simplified for 2-qubit case)
    if num_qubits == 2:
        # For 2-qubit system, calculate entanglement entropy
        state_array = np.array(state_vector)
        # Create density matrix
        rho = np.outer(state_array, np.conj(state_array))
        
        # Partial trace over second qubit
        # Simplified: for 2 qubits, trace out qubit 1
        rho_reduced = np.zeros((2, 2), dtype=complex)
        for i in range(2):
            for j in range(2):
                rho_reduced[i, j] = sum(rho[i*2 + k, j*2 + k] for k in range(2))
        
        # Calculate von Neumann entropy
        eigenvals = np.linalg.eigvals(rho_reduced)
        eigenvals = eigenvals[eigenvals > 1e-10]  # Remove numerical errors
        # Ensure eigenvalues are real (they should be for density matrices)
        eigenvals = np.real(eigenvals)
        entropy = -sum(v * np.log2(v) for v in eigenvals if v > 0)
        metrics["von_neumann_entropy"] = float(np.real(entropy))
        metrics["entanglement_entropy"] = float(np.real(entropy))
    
    # Calculate concurrence (for 2-qubit systems)
    if num_qubits == 2 and len(state_vector) >= 4:
        # Concurrence calculation
        a00 = state_vector[0]
        a01 = state_vector[1]
        a10 = state_vector[2]
        a11 = state_vector[3]
        
        # Simplified concurrence
        concurrence = 2 * abs(a00 * a11 - a01 * a10)
        metrics["concurrence"] = float(concurrence)
    
    return metrics


def create_entanglement_heatmap(state_vector: List[complex], num_qubits: int) -> str:
    """Create ASCII heatmap showing entanglement between qubit pairs."""
    if not state_vector or num_qubits < 2:
        return "Entanglement heatmap requires at least 2 qubits."
    
    lines = ["Entanglement Heatmap (qubit pair correlations):"]
    lines.append("=" * 60)
    
    # Calculate correlation matrix
    metrics = calculate_entanglement_metrics(state_vector, num_qubits)
    
    # Create correlation matrix representation
    lines.append("Qubit Pair Correlation Matrix:")
    lines.append("")
    lines.append("      " + " ".join(f"Q{i}" for i in range(num_qubits)))
    
    # For multi-qubit, show simplified correlations
    if num_qubits == 2:
        concurrence = metrics.get("concurrence", 0.0)
        entropy = metrics.get("entanglement_entropy", 0.0)
        
        lines.append("")
        lines.append("Q0-Q1 Correlation:")
        # Create heatmap bar
        intensity = int(concurrence * 50)
        bar = "█" * intensity + "░" * (50 - intensity)
        lines.append(f"  Concurrence:    {bar} {concurrence:.4f}")
        
        intensity2 = int(entropy * 50)
        bar2 = "█" * intensity2 + "░" * (50 - intensity2)
        lines.append(f"  Entropy:        {bar2} {entropy:.4f}")
    else:
        # For more qubits, show pairwise approximations
        lines.append("")
        for i in range(num_qubits):
            for j in range(i + 1, num_qubits):
                # Simplified: show if states are correlated
                lines.append(f"Q{i}-Q{j}: [Correlation analysis for multi-qubit systems]")
    
    lines.append("")
    lines.append("Legend: █ = High correlation, ░ = Low correlation")
    lines.append("=" * 60)
    return "\n".join(lines)


def create_phase_diagram(state_vector: List[complex], num_qubits: int) -> str:
    """Create text representation of phase diagram."""
    if not state_vector:
        return "No state vector available for phase diagram."
    
    lines = ["Phase Diagram:"]
    lines.append("=" * 80)
    
    # Create phase visualization
    lines.append("Basis State Phase Visualization:")
    lines.append("")
    
    # Group by phase
    phase_data = []
    for i, amplitude in enumerate(state_vector):
        if abs(amplitude) > 1e-10:
            basis_state = format(i, f"0{num_qubits}b")
            phase = math.degrees(math.atan2(amplitude.imag, amplitude.real))
            amp = abs(amplitude)
            phase_data.append((basis_state, phase, amp))
    
    # Sort by phase
    phase_data.sort(key=lambda x: x[1])
    
    # Create circular phase representation
    lines.append("Phase (degrees) vs Amplitude:")
    lines.append("")
    
    for basis_state, phase, amp in phase_data:
        # Normalize phase to 0-360
        phase_norm = phase % 360
        if phase_norm < 0:
            phase_norm += 360
        
        # Create visual representation
        phase_bar_length = int((phase_norm / 360) * 40)
        amp_bar_length = int(amp * 30)
        
        phase_bar = "█" * phase_bar_length
        amp_bar = "█" * amp_bar_length
        
        lines.append(f"|{basis_state}>: Phase={phase:7.2f}° [{phase_bar:<40}] Amp=[{amp_bar}] {amp:.4f}")
    
    lines.append("")
    lines.append("=" * 80)
    return "\n".join(lines)


def create_amplitude_distribution_plot(state_vector: List[complex], num_qubits: int, bins: int = 20) -> str:
    """Create ASCII plot of amplitude distribution."""
    if not state_vector:
        return "No state vector available for amplitude distribution."
    
    lines = ["Amplitude Distribution Plot:"]
    lines.append("=" * 70)
    
    # Extract amplitudes
    amplitudes = [abs(amp) for amp in state_vector if abs(amp) > 1e-10]
    
    if not amplitudes:
        return "No significant amplitudes found."
    
    # Create histogram bins
    min_amp = min(amplitudes)
    max_amp = max(amplitudes)
    bin_width = (max_amp - min_amp) / bins if max_amp > min_amp else 1.0
    
    # Count amplitudes in each bin
    bin_counts = [0] * bins
    for amp in amplitudes:
        if bin_width > 0:
            bin_idx = min(int((amp - min_amp) / bin_width), bins - 1)
        else:
            bin_idx = 0
        bin_counts[bin_idx] += 1
    
    max_count = max(bin_counts) if bin_counts else 1
    
    # Create plot
    lines.append("")
    lines.append("Distribution:")
    lines.append("")
    
    for i in range(bins):
        bin_start = min_amp + i * bin_width
        bin_end = min_amp + (i + 1) * bin_width
        count = bin_counts[i]
        bar_length = int((count / max_count) * 50) if max_count > 0 else 0
        bar = "█" * bar_length
        
        lines.append(f"[{bin_start:.4f}-{bin_end:.4f}]: {bar} {count}")
    
    lines.append("")
    lines.append(f"Statistics:")
    lines.append(f"  Min amplitude: {min_amp:.6f}")
    lines.append(f"  Max amplitude: {max_amp:.6f}")
    lines.append(f"  Mean amplitude: {sum(amplitudes)/len(amplitudes):.6f}")
    lines.append(f"  Total states: {len(amplitudes)}")
    lines.append("=" * 70)
    return "\n".join(lines)


def create_comprehensive_report(
    analysis_result,
    histogram_bins: Optional[int] = None,
    histogram_width: int = 50
) -> str:
    """Create a comprehensive text report with all visualizations."""
    lines = []
    
    # Header
    lines.append("=" * 100)
    lines.append("COMPREHENSIVE QUANTUM CIRCUIT ANALYSIS REPORT")
    lines.append("=" * 100)
    lines.append("")
    
    # Tab 1: Results (Measurement outcomes and probabilities)
    lines.append("┌" + "─" * 98 + "┐")
    lines.append("│" + " " * 30 + "TAB 1: RESULTS" + " " * 53 + "│")
    lines.append("└" + "─" * 98 + "┘")
    lines.append("")
    
    lines.append("Measurement Outcomes and Probabilities:")
    lines.append("-" * 100)
    
    if analysis_result.probabilities:
        lines.append(create_probability_histogram(analysis_result.probabilities, histogram_width, histogram_bins))
    else:
        lines.append("No measurement probabilities available.")
    
    lines.append("")
    lines.append("")
    
    # Tab 2: State (Full quantum state representation)
    lines.append("┌" + "─" * 98 + "┐")
    lines.append("│" + " " * 30 + "TAB 2: STATE" + " " * 54 + "│")
    lines.append("└" + "─" * 98 + "┘")
    lines.append("")
    
    lines.append("Full Quantum State Representation:")
    lines.append("-" * 100)
    
    if analysis_result.state_vector:
        # State vector table
        lines.append(create_state_vector_table(analysis_result.state_vector, analysis_result.qubits, "amplitude"))
        lines.append("")
        lines.append("")
        
        # Bloch sphere representation
        lines.append(create_bloch_sphere_representation(analysis_result.state_vector, analysis_result.qubits))
        lines.append("")
        lines.append("")
        
        # Phase diagram
        lines.append(create_phase_diagram(analysis_result.state_vector, analysis_result.qubits))
        lines.append("")
        lines.append("")
        
        # Amplitude distribution
        lines.append(create_amplitude_distribution_plot(analysis_result.state_vector, analysis_result.qubits))
    else:
        lines.append("No state vector available.")
    
    lines.append("")
    lines.append("")
    
    # Tab 3: Analysis (Metrics and performance indicators)
    lines.append("┌" + "─" * 98 + "┐")
    lines.append("│" + " " * 28 + "TAB 3: ANALYSIS" + " " * 54 + "│")
    lines.append("└" + "─" * 98 + "┘")
    lines.append("")
    
    lines.append("Metrics and Performance Indicators:")
    lines.append("-" * 100)
    
    # Basic metrics
    lines.append("Circuit Metrics:")
    lines.append(f"  Backend: {analysis_result.backend}")
    lines.append(f"  Number of Qubits: {analysis_result.qubits}")
    lines.append(f"  Circuit Depth: {analysis_result.depth}")
    lines.append(f"  Total Operations: {analysis_result.operations}")
    lines.append(f"  Measurements: {analysis_result.measurements}")
    lines.append(f"  Has Measurements: {analysis_result.has_measurements}")
    lines.append("")
    
    lines.append("Operations by Type:")
    for op_type, count in sorted(analysis_result.operations_by_type.items()):
        lines.append(f"  {op_type}: {count}")
    lines.append("")
    
    # Entanglement analysis
    if analysis_result.state_vector and analysis_result.qubits >= 2:
        lines.append(create_entanglement_heatmap(analysis_result.state_vector, analysis_result.qubits))
        lines.append("")
        
        # Entanglement metrics
        metrics = calculate_entanglement_metrics(analysis_result.state_vector, analysis_result.qubits)
        if metrics:
            lines.append("Entanglement Metrics:")
            for metric_name, value in metrics.items():
                lines.append(f"  {metric_name.replace('_', ' ').title()}: {value:.6f}")
            lines.append("")
    
    # Performance indicators
    lines.append("Performance Indicators:")
    if analysis_result.qubits > 0:
        ops_per_qubit = analysis_result.operations / analysis_result.qubits
        lines.append(f"  Operations per Qubit: {ops_per_qubit:.2f}")
    
    if analysis_result.depth > 0:
        ops_per_depth = analysis_result.operations / analysis_result.depth
        lines.append(f"  Operations per Depth Layer: {ops_per_depth:.2f}")
    
    if analysis_result.probabilities:
        max_prob = max(analysis_result.probabilities.values())
        min_prob = min(analysis_result.probabilities.values())
        prob_spread = max_prob - min_prob
        lines.append(f"  Probability Spread: {prob_spread:.6f}")
        lines.append(f"  Max Probability: {max_prob:.6f}")
        lines.append(f"  Min Probability: {min_prob:.6f}")
    
    lines.append("")
    lines.append("=" * 100)
    lines.append("End of Report")
    lines.append("=" * 100)
    
    return "\n".join(lines)

