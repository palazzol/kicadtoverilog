module TestIC_kicad_sch(
    input CLK,
    output Q,
    output ~{Q});

    // TBD wires

    74LS02 U1(/* */);
    74LS02 U2(/* */);
    inv_kicad_sch inv(/* */);
    inv_kicad_sch inv1(/* */);
endmodule
