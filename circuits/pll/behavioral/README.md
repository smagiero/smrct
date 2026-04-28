# PLL Behavioral Models

Two behavioral PLL models written in synthesizable-subset SystemVerilog using
a `real`-typed VFO delay to expose analog frequency control behaviour.
No PDK required. Targets iverilog + GTKWave.

## Models

### pll_jerky_behav.v
Single-cycle phase detector (pll_jerky_pd). Makes a VFO adjust decision on
every ClockIn edge based on PLLClock high-count in the previous half-period.
Fast but noisy — intentionally "jerky".

### pll_avg_behav.v
Averaging phase detector (pll_avg_pd). Accumulates edge decisions over a
2^(N+1)-cycle window (N=3, so 16 cycles) before adjusting the VFO.
Smoother lock behaviour. VFO frequency clamped to [VFO_Min, VFO_Max].

## Simulation

From circuits/pll/sim/ (executables and VCDs are written here and git-ignored):

  iverilog -s pll_jerky_tb -g2012 -Wall \
    -Wno-sensitivity-entire-vector -Wno-sensitivity-entire-array \
    -o pll_jerky ../tb/pll_jerky_tb.v && ./pll_jerky

  iverilog -s pll_avg_tb -g2012 -Wall \
    -Wno-sensitivity-entire-vector -Wno-sensitivity-entire-array \
    -o pll_avg ../tb/pll_avg_tb.v && ./pll_avg

  surfer pll_jerky.vcd
  surfer pll_avg.vcd
