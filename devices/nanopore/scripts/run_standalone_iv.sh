#!/bin/bash
# Nanopore I-V Standalone Simulation Script
# Sebastian Claudiusz Magierowski Nov 23 2025
# Runs Spectre simulation directly using cad-spec

# Exit on error
set -e

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DEVICE_DIR="$(dirname "$SCRIPT_DIR")"

# Paths
NETLIST="$DEVICE_DIR/testbenches/standalone/tb_iv.scs"
RESULTS_DIR="$DEVICE_DIR/results/standalone/iv"
LOG_FILE="$RESULTS_DIR/spectre.log"

# Create results directory
mkdir -p "$RESULTS_DIR"

# Print info
echo "=================================================="
echo "Nanopore I-V Standalone Simulation"
echo "=================================================="
echo "Netlist:      $NETLIST"
echo "Results dir:  $RESULTS_DIR"
echo "Log file:     $LOG_FILE"
echo "=================================================="

# Run Spectre
cd "$RESULTS_DIR"
cad-spec "$NETLIST" =log "$LOG_FILE"

# Check for success
if [ $? -eq 0 ]; then
    echo ""
    echo "Simulation completed successfully!"
    echo "Results available in: $RESULTS_DIR"
    echo ""
    echo "To analyze results, run:"
    echo "  python3 $SCRIPT_DIR/analyze_iv.py"
else
    echo ""
    echo "ERROR: Simulation failed. Check log file:"
    echo "  $LOG_FILE"
    exit 1
fi
