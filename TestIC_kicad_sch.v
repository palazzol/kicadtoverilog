module TestIC_kicad_sch(
    output ~{Q},
    input CLK,
    output Q);

    wire w1;
    wire w2;
    wire w3;
    wire w4;
    wire w5;

    NOR2 U2(/* */);
    NOR2 U1(/* */);
    inv_kicad_sch inv(/* */);
    inv_kicad_sch inv1(/* */);
endmodule
