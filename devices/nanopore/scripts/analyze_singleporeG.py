#!/usr/bin/env python3
# Sebastian Claudiusz Magierowski May 4 2026
"""Nanopore + CT TIA analysis — reads tb_singleporeG.raw/tran1.tran.tran (psfascii).

Plots TIA output voltage and pore current vs time.

Note on output resolution: Spectre's adaptive stepper with errpreset=moderate
takes large time steps (~200 µs) during quasi-DC intervals between events,
producing sparse output (~100 pts for a 10 ms run).  The TIA bandwidth is
~1/2πRfCf ≈ 1.6 kHz (Rf=1 GΩ, Cf=100 fF), so the dominant time constant
is ~100 µs — just resolved at 200 µs output spacing.  To increase output
density, reduce tstep in tb_singleporeG.scs.
"""

import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from psf_utils import PSF

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_RAW = os.path.join(
    SCRIPT_DIR,
    "../results/standalone/singleporeG/tb_singleporeG.raw/tran1.tran.tran",
)
OUT_DIR = os.path.join(SCRIPT_DIR, "../results/standalone/singleporeG")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=DEFAULT_RAW)
    args = ap.parse_args()

    psf = PSF(args.raw)
    t = psf.get_sweep().abscissa
    # AMporeout is a 0-V source ammeter; :p is current into its + terminal.
    # Pore current flows from bias through pore into AMporeout's + terminal → gnd,
    # so ipore = AMporeout:p (positive = current entering TIA virtual ground).
    ipore = psf.get_signal("AMporeout:p").ordinate
    vout = psf.get_signal("out1").ordinate

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    axes[0].plot(t * 1e3, vout * 1e3)
    axes[0].set_ylabel("TIA Output (mV)")
    axes[0].set_title("Nanopore + CT TIA  (Rf = 1 GΩ, random ctrl events at 1 kHz mean)")
    axes[0].grid(True)

    axes[1].plot(t * 1e3, ipore * 1e12)
    axes[1].set_xlabel("Time (ms)")
    axes[1].set_ylabel("Pore Current (pA)")
    axes[1].grid(True)

    fig.tight_layout()
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "singleporeG.png")
    fig.savefig(out, dpi=150)
    print(f"Saved {out}")
    print(f"  Time: 0 to {t[-1]*1e3:.1f} ms  ({len(t)} pts)")
    print(f"  Vout: {vout.min()*1e3:.1f} to {vout.max()*1e3:.1f} mV")
    print(f"  Ipore: {ipore.min()*1e12:.1f} to {ipore.max()*1e12:.1f} pA")


if __name__ == "__main__":
    main()
