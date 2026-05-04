#!/usr/bin/env python3
# Sebastian Claudiusz Magierowski May 4 2026
"""Nanopore transient analysis — reads tb_tran.raw/tran1.tran.tran (psfascii)."""

import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from psf_utils import PSF

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_RAW = os.path.join(
    SCRIPT_DIR, "../results/standalone/tran/tb_tran.raw/tran1.tran.tran"
)
OUT_DIR = os.path.join(SCRIPT_DIR, "../results/standalone/tran")


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
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "tran.png")
    fig.savefig(out, dpi=150)
    print(f"Saved {out}")
    print(f"  Time: 0 to {t[-1]*1e9:.0f} ns  ({len(t)} pts)")
    tau = 2.25e9 * 5e-12
    print(f"  RC time constant: Ravg*Cm = {tau*1e3:.2f} ms  (sim window << τ)")


if __name__ == "__main__":
    main()
