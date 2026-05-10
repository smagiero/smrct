#!/usr/bin/env python3
# Sebastian Claudiusz Magierowski May 3 2026
"""Nanopore DC I-V analysis — reads tb_iv.raw/dc1.dc (psfascii).

Simulation parameters (Ravg) are parsed directly from tb_iv.scs,
which is the single source of truth.
"""

import os
import re
import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from psf_utils import PSF

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
REPO_DIR    = os.path.join(SCRIPT_DIR, "../../..")
WATERMARK   = os.path.join(REPO_DIR, "docs", "emil_tran.png")
DEFAULT_RAW = os.path.join(SCRIPT_DIR, "../results/standalone/iv/tb_iv.raw/dc1.dc")
DEFAULT_SCS = os.path.join(SCRIPT_DIR, "../testbenches/standalone/tb_iv.scs")
OUT_DIR     = os.path.join(SCRIPT_DIR, "../results/standalone/iv")

_SPECTRE_SUFFIXES = {
    'f': 1e-15, 'p': 1e-12, 'n': 1e-9, 'u': 1e-6,
    'm': 1e-3,  'k': 1e3,   'M': 1e6,  'G': 1e9,  'T': 1e12,
}


def parse_spectre_params(scs_path):
    """Return dict of floats from all 'parameters' lines in a Spectre netlist."""
    with open(scs_path) as fh:
        text = fh.read()
    text = re.sub(r'\\\n', ' ', text)

    def _sub_suffix(m):
        return f"({m.group(1)}*{_SPECTRE_SUFFIXES[m.group(2)]})"

    params = {}
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith('parameters'):
            continue
        rest = re.sub(r'//.*', '', line[len('parameters'):]).strip()
        for m in re.finditer(r'(\w+)\s*=\s*(\S+)', rest):
            key, val_str = m.group(1), m.group(2)
            val_py = re.sub(
                r'(\d+\.?\d*(?:[eE][+-]?\d+)?)([fpnumkMGT])\b',
                _sub_suffix,
                val_str,
            )
            try:
                params[key] = float(eval(val_py, {"__builtins__": {}}, params))
            except Exception:
                pass
    return params


def _add_watermark(fig):
    if os.path.exists(WATERMARK):
        wm_ax = fig.add_axes([0.1, 0.15, 0.75, 0.75], anchor='C', zorder=10)
        wm_ax.imshow(mpimg.imread(WATERMARK), alpha=0.08)
        wm_ax.axis('off')


# Load simulation parameters from testbench — single source of truth
_p   = parse_spectre_params(DEFAULT_SCS)
RAVG = _p['Ravg']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=DEFAULT_RAW)
    args = ap.parse_args()

    psf = PSF(args.raw)
    vbias = psf.get_sweep().abscissa
    # V1:p is current INTO V1's + terminal; pore current = -V1:p
    ipore = -psf.get_signal("V1:p").ordinate

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    axes[0].plot(vbias, ipore * 1e9)
    axes[0].set_xlabel("Bias (V)")
    axes[0].set_ylabel("Pore Current (nA)")
    axes[0].set_title("Nanopore I-V  (ctrl = 0)")
    axes[0].grid(True)

    # Conductance G = I/V, skip points near zero
    mask = np.abs(vbias) > 0.05
    G = ipore[mask] / vbias[mask]
    axes[1].plot(vbias[mask], G * 1e9)
    axes[1].set_xlabel("Bias (V)")
    axes[1].set_ylabel("Conductance (nS)")
    axes[1].set_title(f"G = I/V  (mean {G.mean()*1e9:.4f} nS)")
    axes[1].grid(True)

    fig.tight_layout()
    _add_watermark(fig)
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "iv.png")
    fig.savefig(out, dpi=150)
    print(f"Saved {out}")
    print(f"  Vbias: {vbias.min():.2f} to {vbias.max():.2f} V  ({len(vbias)} pts)")
    print(f"  Mean G: {G.mean()*1e9:.4f} nS  (1/Ravg = {1/RAVG*1e9:.4f} nS expected)")


if __name__ == "__main__":
    main()
