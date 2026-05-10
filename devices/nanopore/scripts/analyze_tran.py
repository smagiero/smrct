#!/usr/bin/env python3
# Sebastian Claudiusz Magierowski May 4 2026
"""Nanopore transient analysis — reads tb_tran.raw/tran1.tran.tran (psfascii).

Simulation parameters (Ravg, Cm) are parsed directly from tb_tran.scs,
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
DEFAULT_RAW = os.path.join(SCRIPT_DIR, "../results/standalone/tran/tb_tran.raw/tran1.tran.tran")
DEFAULT_SCS = os.path.join(SCRIPT_DIR, "../testbenches/standalone/tb_tran.scs")
OUT_DIR     = os.path.join(SCRIPT_DIR, "../results/standalone/tran")

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
CM   = _p['Cm']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=DEFAULT_RAW)
    args = ap.parse_args()

    psf = PSF(args.raw)
    t = psf.get_sweep().abscissa
    vbias = psf.get_signal("bias").ordinate
    ipore = -psf.get_signal("V1:p").ordinate

    fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

    axes[0].plot(t * 1e9, vbias)
    axes[0].set_ylabel("Bias (V)")
    axes[0].set_title("Nanopore Transient  (ctrl = 0, RC charging via Ravg ∥ Cmem)")
    axes[0].grid(True)

    axes[1].plot(t * 1e9, ipore * 1e9)
    axes[1].set_xlabel("Time (ns)")
    axes[1].set_ylabel("Pore Current (nA)")
    axes[1].grid(True)

    fig.tight_layout()
    _add_watermark(fig)
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "tran.png")
    fig.savefig(out, dpi=150)
    print(f"Saved {out}")
    print(f"  Time: 0 to {t[-1]*1e9:.0f} ns  ({len(t)} pts)")
    tau = RAVG * CM
    print(f"  RC time constant: Ravg*Cm = {tau*1e3:.2f} ms  (sim window << τ)")


if __name__ == "__main__":
    main()
