module kicadtoverilog_test(
);

    wire net_1;
    wire net_2;
    wire net_3;
    wire net_4;
    wire net_5;
    wire net_6;
    wire net_7;

    GND #PWR0102(.GND(net_3));
    +5V #PWR0101(.+5V(net_2));
    LED D1(.K(net_1), .A(net_6));
    DGOF5S3 X1(.Vcc(net_2), .GND(net_3), .OUT(net_4));
    GND #PWR0103(.GND(net_1));
    GND #PWR0104(.GND(net_5));
    LED D2(.K(net_5), .A(net_7));
    TestIC TestIC(.CLK(net_4), .Q(net_6), .not_Q(net_7));
endmodule
