module TestIC_kicad_sch(
    output not_Q,
    input CLK,
    output Q);

    wire net_1;
    wire net_2;

    NOR2 U1(CLK, net_2, net_1);
    NOR2 U2(net_1, CLK, net_2);
    inv_kicad_sch inv(.A(net_1), .Y(Q));
    inv_kicad_sch inv1(.A(net_2), .Y(not_Q));
endmodule
