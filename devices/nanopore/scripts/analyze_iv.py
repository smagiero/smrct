#!/usr/bin/env python3
# Sebastian Claudiusz Magierowski May 3 2026
"""Nanopore DC I-V analysis — reads tb_iv.raw/dc1.dc (psfascii)."""

import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from psf_utils import PSF

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_RAW = os.path.join(
    SCRIPT_DIR, "../results/standalone/iv/tb_iv.raw/dc1.dc"
)
OUT_DIR = os.path.join(SCRIPT_DIR, "../results/standalone/iv")


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
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "iv.png")
    fig.savefig(out, dpi=150)
    print(f"Saved {out}")
    print(f"  Vbias: {vbias.min():.2f} to {vbias.max():.2f} V  ({len(vbias)} pts)")
    print(f"  Mean G: {G.mean()*1e9:.4f} nS  (1/Ravg = {1/2.25e9*1e9:.4f} nS expected)")


if __name__ == "__main__":
    main()
