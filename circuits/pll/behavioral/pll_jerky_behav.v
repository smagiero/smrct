//========================================================================
// circuits/pll/behavioral/pll_jerky_behav.v
//========================================================================
// Sebastian Claudiusz Magierowski Aug 9 2023
//
// Keeping PLLClock phase locked to ClockIn.  COMP tracks how long PLLClock
// is high (counts number of PLLClock edges in ClockIn half-period) while
// ClockIn is high.  If there's lots of PLLClock edges being counted, you
// should slow the VFO down, and if there's few (none) PLLClock edges being
// counted you should speed the VFO up.
//
`ifndef PLL_JERKY
`define PLL_JERKY
//
//                Reset                    Reset
//                  |                        |
//                  V                        V
// (ref clk)    --------                  -------
// ClockIn ---->|      |                  |     |
//              | COMP |--> AdjustFreq -->| VFO |--> CLockOut --+-->
// PLLClock +-->|      |                  |     |               |
//          |   --------                  -------               |
//          +--------------------- VFOOUt ----------------------+
//
//========================================================================
// PLL
//========================================================================
module pll_jerky
(
  input  Reset,
  input  ClockIn,
  output ClockOut
);

  logic [1:0] AdjFreq;
  logic VFOOut;

  assign ClockOut = VFOOut;

  pll_jerky_pd comp (.AdjustFreq(AdjFreq), .ClockIn(ClockIn),
                     .PLLClock(VFOOut), .Reset(Reset) );

  pll_jerky_vfo osc (.ClockOut(VFOOut), .AdjustFreq(AdjFreq), .Reset(Reset) );

endmodule // pll_jerky

//========================================================================
// PD (phase comparator)
//========================================================================
//             ______
// ClockIn --->|    |
//             | PD |--> Adjr --> AdjustFreq
// PLLClock -->|    |
//             ------
//
module pll_jerky_pd
(
  input  logic Reset,
  input  logic ClockIn,
  input  logic PLLClock,
  output logic [1:0] AdjustFreq
);

  logic [1:0] Adjr;
  logic [2:0] HiCount;

  assign AdjustFreq = Adjr;

  always@(ClockIn, Reset)           // when the ref clk (or reset) changes…
    if (Reset == 1'b1) begin        // if it's a reset…
      Adjr    = 2'b01;              // …keep VFO freq same
      HiCount = 3'b000;             // …zero HiCount
    end else if (PLLClock == 1'b1)  // if i/p clk is high
      HiCount = HiCount + 3'b001;   // …inc HiCount
    else begin                      // if i/p clk is low…
      case (HiCount)                // …decide what to do to VFO based on the HiCount (while PLLClock was high)
	      3'b000:  Adjr = 2'b00;      // INC VFO freq (you didn't register a single PLL hi)
	      3'b001:  Adjr = 2'b01;      // keep freq same
        default: Adjr = 2'b11;      // DEC VFO freq (you registered too many PLL hi)
      endcase
      HiCount = 3'b000;             // …reset HiCount after PLLClock goes lo
    end

endmodule // pll_jerky_pd

//========================================================================
// VFO (variable frequency oscillator)
//========================================================================
module pll_jerky_vfo
(
  input logic Reset,
  input logic [1:0] AdjustFreq,
  output logic ClockOut
);

  logic PLLClock;
  real VFO_Delay;

  assign ClockOut = PLLClock;

  always@(PLLClock, Reset)
    if (Reset == 1'b1) begin
      VFO_Delay = `VFOBaseDelay;
      PLLClock  = 1'b0;
    end else begin
      if ( (AdjustFreq==2'b11) && (VFO_Delay > `VFO_Min) )
        VFO_Delay = VFO_Delay - `VFO_Delta; // speed VFO up
      else if ( (AdjustFreq==2'b00) && (VFO_Delay < `VFO_Max) )
        VFO_Delay = VFO_Delay + `VFO_Delta; // slow VFO down
      // else, leave VFO_Delay alone.
      #VFO_Delay PLLClock <= ~PLLClock;
    end

endmodule // pll_jerky_vfo

`endif /* PLL_JERKY */
