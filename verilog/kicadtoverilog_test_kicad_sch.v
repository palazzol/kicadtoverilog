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
    LED D1(net_6, net_1);
    DGOF5S3 X1(wire_NC, net_3, net_2, net_4);
    GND #PWR0103(net_1);
    GND #PWR0104(net_5);
    LED D2(net_7, net_5);
    TestIC_kicad_sch TestIC(net_4, net_6, net_7);
endmodule
