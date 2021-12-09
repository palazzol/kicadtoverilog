module TestIC(
    output not_Q,
    input CLK,
    output Q);

    wire net_1;
    wire net_2;

    NOR2 U1(.A(CLK), .B(net_2), .Y(net_1));
    NOR2 U2(.A(net_1), .B(CLK), .Y(net_2));
    inv inv1(.A(net_1), .Y(Q));
    inv inv2(.A(net_2), .Y(not_Q));
endmodule
