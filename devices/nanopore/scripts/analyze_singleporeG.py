#!/usr/bin/env python3
# Sebastian Claudiusz Magierowski May 4 2026
"""Nanopore + CT TIA analysis — reads tb_singleporeG.raw/tran1.tran.tran (psfascii).

Computes:
  - Time-domain traces: Ipore (pA) and Vout (mV)
  - Normalised pore-current PSD vs theoretical Lorentzian for a random telegraph signal

PSF parameters assumed (must match tb_singleporeG.scs):
  fsamp  = 25*ft = 25 kHz   (output strobe period = 40 µs)
  samples = 65536            (2^16, gives clean FFT)
  winsize = samples/32 = 2048 (Welch segment length, ~32 averages)
  Skip first 1 % of samptime before computing statistics and PSD.

Theoretical normalised PSD for a Poisson random telegraph signal:
  ft * S_norm(f) = 1 / (1 + (pi*f/ft)^2)
  Corner at f = ft/pi ~ 318 Hz; -20 dB/decade above corner (dB20 scale).
  Reference stored value from original Virtuoso run: IporeStdDev_pA = 30.853 pA.
"""

import os
import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import welch
from psf_utils import PSF

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_RAW = os.path.join(
    SCRIPT_DIR,
    "../results/standalone/singleporeG/tb_singleporeG.raw/tran1.tran.tran",
)
OUT_DIR = os.path.join(SCRIPT_DIR, "../results/standalone/singleporeG")

# Match tb_singleporeG.scs parameters
FT      = 1e3        # mean event rate (Hz)
FSAMP   = 25 * FT    # output sample rate (Hz)
SAMPLES = 65536      # total output samples
WINSIZE = SAMPLES // 32   # Welch segment length (2048)
SKIP    = int(0.01 * SAMPLES)  # drop first 1 % (~655 samples) for settling


def load(raw_path):
    psf = PSF(raw_path)
    t     = psf.get_sweep().abscissa
    ipore = psf.get_signal("AMporeout:p").ordinate
    vout  = psf.get_signal("out1").ordinate
    return t, ipore, vout


def plot_time(t, ipore, vout, out_dir):
    fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    axes[0].plot(t * 1e3, vout * 1e3, lw=0.6)
    axes[0].set_ylabel("TIA Output (mV)")
    axes[0].set_title(f"Nanopore + CT TIA  (Rf=1GΩ, ft={FT/1e3:.0f} kHz, {len(t)} pts)")
    axes[0].grid(True)
    axes[1].plot(t * 1e3, ipore * 1e12, lw=0.6)
    axes[1].set_xlabel("Time (ms)")
    axes[1].set_ylabel("Pore Current (pA)")
    axes[1].grid(True)
    fig.tight_layout()
    path = os.path.join(out_dir, "singleporeG_time.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Saved {path}")


def plot_psd(ipore, vout, out_dir):
    ip = ipore[SKIP:]
    vo = vout[SKIP:]

    sigma_I = np.std(ip)
    sigma_V = np.std(vo)
    print(f"  IporeStdDev_pA : {sigma_I*1e12:.3f} pA  (reference: 30.853 pA)")
    print(f"  Vout1StdDev    : {sigma_V*1e3:.3f} mV  (reference: 30.790 mV)")


    # Divide by sigma, giving signal unit variance, so the Lorentzian theory is 0 dB at DC and -6 dB at corner.
    # i.e., one-sided returned by default by welch gives: ∫₀^{f_Nyq} S_I(f) df = 1 
    f_I, S_I = welch(ip / sigma_I, fs=FSAMP, window='boxcar', nperseg=WINSIZE, detrend=False)
    f_V, S_V = welch(vo / sigma_V, fs=FSAMP, window='boxcar', nperseg=WINSIZE, detrend=False)
    # Normalised double-sided PSD: (ft/2) * S_one / sigma^2 = ft * S_two / sigma^2
    # the (FT/2) factor converts scipy's one-sided S_one to the two-sided S_two (S_one = 2*S_two for f>0).
    norm_I_dB = 20 * np.log10((FT/2) * S_I + 1e-30)
    norm_V_dB = 20 * np.log10((FT/2) * S_V + 1e-30)

    # Theoretical double-sided normalised Lorentzian for a toggle RTS:
    #   ft * S_two(f) / sigma^2 = 1 / (1 + (pi*f/ft)^2)
    # DC value: 0 dB.  Corner (−6 dB20): f = ft/pi ~ 318 Hz.
    f_th = np.logspace(np.log10(f_I[1]), np.log10(FSAMP/2), 2000)
    S_th_dB = 20 * np.log10(1.0 / (1 + (np.pi * f_th / FT)**2))

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for ax, f_sim, S_dB, label in [
        (axes[0], f_I, norm_I_dB, "Pore current"),
        (axes[1], f_V, norm_V_dB, "TIA output"),
    ]:
        ax.semilogx(f_sim[1:], S_dB[1:], lw=0.8, label="Simulation")
        ax.semilogx(f_th, S_th_dB, 'r--', lw=1.5, label="Lorentzian theory")
        ax.axvline(FT/np.pi, color='gray', ls=':', lw=1,
                   label=f"Corner ft/π = {FT/np.pi:.0f} Hz")
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Normalised PSD  dB20(ft · S_two / σ²)")
        ax.set_title(f"{label} — normalised PSD")
        ax.set_xlim(f_I[1], FSAMP/2)
        ax.set_ylim(-60, 20)
        ax.legend(fontsize=8)
        ax.grid(True, which='both', ls=':')

    fig.tight_layout()
    path = os.path.join(out_dir, "singleporeG_psd.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Saved {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=DEFAULT_RAW)
    args = ap.parse_args()

    t, ipore, vout = load(args.raw)
    print(f"  Loaded {len(t)} points, "
          f"t = 0 to {t[-1]*1e3:.1f} ms  (expected ~{SAMPLES} pts at {1/FSAMP*1e6:.0f} µs)")

    os.makedirs(OUT_DIR, exist_ok=True)
    plot_time(t, ipore, vout, OUT_DIR)
    plot_psd(ipore, vout, OUT_DIR)


if __name__ == "__main__":
    main()
