<div align="center">

<picture>
  <img alt="emilrc" src="docs/emil_tran.png" width="30%" height="30%">
</picture>

</div>

# smrct | ICs for the people

---

## Repository Structure

This repository contains analog/mixed-signal IC design projects with support for both **standalone Spectre workflows** (primary, command-line driven) and **OCEAN/GUI workflows** (legacy, Virtuoso-based).

### Organization

```
smrct/
├── models/verilogA/          # Device models (Verilog-A)
├── devices/                  # Device-level designs
│   └── nanopore/
│       ├── netlist/          # Shared subcircuit definitions
│       ├── testbenches/
│       │   ├── standalone/   # Primary: Self-contained Spectre testbenches
│       │   └── ocean/        # Legacy: OCEAN-compatible netlists
│       ├── scripts/
│       │   ├── *.sh         # Standalone simulation scripts (cad-spec)
│       │   ├── *.py         # Analysis/post-processing scripts
│       │   └── legacy/      # OCEAN scripts (.ocn files)
│       └── results/
│           ├── standalone/   # Results from standalone workflows
│           └── ocean/        # Results from OCEAN workflows
├── circuits/                 # Circuit-level designs (future)
├── systems/                  # System-level designs (future)
├── lib/                      # Shared libraries and utilities
└── docs/                     # Documentation

```

### Workflows

#### Standalone Workflow (Primary)

Command-line driven workflow using `cad-spec` directly:

```bash
# Navigate to device directory
cd devices/nanopore

# Run I-V characterization
./scripts/run_standalone_iv.sh

# Analyze results (placeholder - to be implemented)
./scripts/analyze_iv.py
```

**Advantages:**
- Fully scriptable and automatable
- Version control friendly
- No GUI dependencies
- Faster iteration for batch simulations

#### OCEAN Workflow (Legacy)

GUI-driven workflow using Virtuoso ADE and OCEAN:

```bash
# Navigate to device directory
cd devices/nanopore

# Run OCEAN script
ocean -nograph -replay scripts/legacy/run_iv.ocn
```

**Use cases:**
- Integration with existing Virtuoso projects
- Interactive waveform viewing
- ADE Explorer compatibility

### Getting Started

1. **Models**: VerilogA models are in `models/verilogA/`
2. **Devices**: Device-level testbenches are in `devices/*/testbenches/standalone/`
3. **Simulation**: Run standalone scripts from `devices/*/scripts/`
4. **Results**: Check `devices/*/results/standalone/` for output

### Guidelines

- **Primary workflow**: Use standalone Spectre testbenches for new designs
- **Version control**: All netlists, scripts, and models are tracked; results are ignored
- **File organization**: Keep subcircuit definitions in `netlist/`, testbenches in `testbenches/standalone/`
- **Scripts**: Place simulation drivers in `scripts/`, analysis tools alongside

---