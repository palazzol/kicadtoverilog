module TestIC_kicad_sch(
    output ~{Q},
    input CLK,
    output Q);

    wire net_1;
    wire net_2;

    NOR2 U1(net_2, CLK, net_1);
    NOR2 U2(CLK, net_1, net_2);
    inv_kicad_sch inv(net_1, Q);
    inv_kicad_sch inv1(net_2, ~{Q});
endmodule
