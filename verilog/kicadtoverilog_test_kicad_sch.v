module kicadtoverilog_test_kicad_sch(
);

    wire net_1;
    wire net_2;
    wire net_3;
    wire net_4;
    wire net_5;
    wire net_6;
    wire net_7;

    GND #PWR0102(net_3);
    +5V #PWR0101(net_2);
    LED D1(net_1, net_6);
    DGOF5S3 X1(wire_NC, net_2, net_3, net_4);
    GND #PWR0103(net_1);
    GND #PWR0104(net_5);
    LED D2(net_5, net_7);
    TestIC_kicad_sch TestIC(.CLK(net_4), .Q(net_6), .not_Q(net_7));
endmodule
