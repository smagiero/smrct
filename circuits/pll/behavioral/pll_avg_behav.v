//========================================================================
// circuits/pll/behavioral/pll_avg_behav.v
//========================================================================
// Sebastian Claudiusz Magierowski Aug 9 2023
//
// Pretty similar to the basic PLL, but instead of just counting PLLClock
// edges within ClockIn half-periods, it averages the edge count over a
// 2^(N+1)-cycle window before adjusting the VFO.

`ifndef PLL_AVG
`define PLL_AVG
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
module pll_avg
(
  input  Reset,
  input  ClockIn,
  output ClockOut
);

  logic [1:0] AdjFreq;
  logic VFOOut;

  assign ClockOut = VFOOut;

  pll_avg_pd comp (.AdjustFreq(AdjFreq), .ClockIn(ClockIn),
                   .PLLClock(VFOOut), .Reset(Reset) );

  pll_avg_vfo osc (.ClockOut(VFOOut), .AdjustFreq(AdjFreq), .Reset(Reset) );

endmodule // pll_avg

//========================================================================
// pll_avg_pd
//========================================================================
//   count edges (CE) of PLLClock
//             ______
// ClockIn --->|    |
//             | CE |--> EdgeCode --+  avgerage edges
// PLLClock -->|    |               |  over a window &
//             ------               |  make decision (MD)
//                                  |    ______
//                                  +--> |    |
//                                       | MD |-> Adjr --> AdjustFreq
// ClockIn ----------------------------> |    |
//                                       ------
module pll_avg_pd
(
  input logic Reset,
  input logic ClockIn,
  input logic PLLClock,
  output[1:0] AdjustFreq
);

  localparam N = 3;          // 2^(N+1) is averager resolution.
  localparam InitAvg = 1<<N; // Midpoint value for AvgEdge (InitAvg=8)
  //
  logic [1:0] Adjr;

  assign AdjustFreq = Adjr;

  // -------------------------------
  // Sanity-check assertion:
  `ifdef DC
  `else
  initial
    if (N<3)
      begin
      $display("%m: pll_avg_pd averager width=%d is too low.", N);
      $display("%m: Cannot simulate this design.");
      $finish;
      end
  `endif
  // -------------------------------
  //
  logic [2:0]   HiCount;  // Counts PLL highs per ClockIn.
  logic [1:0]   EdgeCode; // Locally encodes edge decision.
  logic [N:0]   AvgEdge;  // Decision variable.
  logic [N-1:0] Done;     // Decision trigger variable.
  //
  // Count Edges (CE)
  // The first always block is edge-oriented:
  // The value of EdgeCode is used to increment or decrement AvgEdge
  always@(ClockIn, Reset) begin : CheckEdges
    if (Reset == 1'b1) begin
      EdgeCode = 2'b01;
      HiCount  =  'b0;
    end
    else if (PLLClock==1'b1) // Should be 1 of these per ClockIn cycle.
      HiCount = HiCount + 3'b1;
    else begin// Check to see how many PLL 1's we caught:
      case (HiCount)
        3'b000:  EdgeCode = 2'b00; // Didn't count a PLL hi, PLL too fast
        3'b001:  EdgeCode = 2'b01; // Seems matched.
        default: EdgeCode = 2'b11; // Counted 2+ PLL hi, PLL too slow
      endcase
      HiCount = 'b0; // Initialize for next ClockIn edge.
    end
  end // CheckEdges.
  //
  // Make Decision (MD)
  // The second always block is decision-oriented:
  always@(ClockIn, Reset) begin : MakeDecision
    if (Reset == 1'b1) begin
      Adjr    = 2'b1; // No change code.
      Done    =  'b0;
      AvgEdge =  InitAvg;
    end
    else begin // Update the AvgEdge & check for decision:
      case (EdgeCode)
        2'b00: AvgEdge = AvgEdge - 1; // Add to PLL edge count.
        2'b11: AvgEdge = AvgEdge + 1; // Sub from PLL edge count.
        // default: do nothing.
      endcase
      Done = Done + 1;
      if (Done == 'b0) begin // Wrap-around.
        if ( AvgEdge < (InitAvg-1) )
          Adjr = 2'b00; // PLL too fast, better slow it down.
        else if ( AvgEdge>(InitAvg+1) )
          Adjr = 2'b11; // PLL too slow, better speed it up.
        else Adjr = 2'b01; // No change.
          AvgEdge = InitAvg; // Initialize for next Done.
      end
    end
  end // MakeDecision.
  //
endmodule // pll_avg_pd.

//========================================================================
// pll_avg_vfo
//========================================================================
module pll_avg_vfo (output ClockOut, input[1:0] AdjustFreq, input Reset);
  reg PLLClock;
  real VFO_Delay;
  //
  assign ClockOut = PLLClock;
  //
  always@(PLLClock, Reset)
    if (Reset==1'b1) begin
      VFO_Delay = `VFOBaseDelay;
      PLLClock  = 1'b0;
    end else begin
    if ( (AdjustFreq==2'b00) && (VFO_Delay < `VFO_Max) )      // if need to slow down VFO & its not already at min freq
      VFO_Delay = VFO_Delay + `VFO_Delta; // slow VFO down
    else if ( (AdjustFreq==2'b11) && (VFO_Delay > `VFO_Min) ) // if need to speed up VFO & its not already at max freq
      VFO_Delay = VFO_Delay - `VFO_Delta; // speed VFO up
    // else, leave VFO_Delay alone.
    #VFO_Delay PLLClock <= ~PLLClock;     // adjusted VFO frequency
  end

endmodule // pll_avg_vfo.

`endif /* PLL_AVG */
