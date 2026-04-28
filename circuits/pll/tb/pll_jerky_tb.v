//========================================================================
// circuits/pll/tb/pll_jerky_tb.v
//========================================================================
// Sebastian Claudiusz Magierowski Aug 9 2023
//
// HalfPeriod --
//  _   _       \         _______                        _____
// | |_| |_ TstClock --> | delay | --> ClockIntStim --> | PLL | --> PLLClockOut
//                        -------                        -----
//
`timescale 1ns/10ps

// to run in iverilog (from circuits/pll/sim/):
// iverilog -s pll_jerky_tb -g2012 -Wall -Wno-sensitivity-entire-vector -Wno-sensitivity-entire-array -o pll_jerky ../tb/pll_jerky_tb.v
// ./pll_jerky
// surfer pll_jerky.vcd

`define VFO_Delta    0.001  // ns.
//
`define ClockHalfPeriod 1.25   // ns half-period at 400 MHz.
`define VFOBaseDelay `ClockHalfPeriod
`define VFO_Max (`VFOBaseDelay*1.0 + 0.250)
`define VFO_Min (`VFOBaseDelay*1.0 - 0.250)

`include "../behavioral/pll_jerky_behav.v"

module pll_jerky_tb();

logic  ClockInStim, PLLClockOut;
logic TstClock, Reset, DriftDirection;
logic [7:0] DriftClock;
real  HalfPeriod;

assign #0.5 ClockInStim = TstClock;

// Implement the clock:
always@(TstClock) begin
  #HalfPeriod TstClock <= ~TstClock;
  DriftClock <= DriftClock + 7'h1;   // inc DriftClock twice per TstClock period
end

// Drift the clock:
// after 2^6/2 = 32 cycles,
// every 2^7=64 cycles,
// change input clock period
always@(posedge DriftClock[7]) begin
  if (DriftDirection == 1'b1)
    HalfPeriod = HalfPeriod + 0.01;
  else
    HalfPeriod = HalfPeriod - 0.01;
  // change direction of period change
  if ( HalfPeriod >= (`ClockHalfPeriod+0.100) )
    DriftDirection = 1'b0;
  if ( HalfPeriod <= (`ClockHalfPeriod-0.100) )
    DriftDirection = 1'b1;
  end

initial begin
  $dumpfile("pll_jerky.vcd");
  $dumpvars;

  Reset          = 1'b0;
  HalfPeriod     = `ClockHalfPeriod*1.0 + 0.000;
  DriftDirection = 1'b1;
  DriftClock     =  'b0;
  #1  TstClock   = 1'b0;
  #1  Reset      = 1'b1;
  #18 Reset      = 1'b0;
  #30000 $finish;
end

pll_jerky PLL1 (.ClockOut(PLLClockOut), .ClockIn(ClockInStim), .Reset(Reset));

endmodule
