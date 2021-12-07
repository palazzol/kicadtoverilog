module test_kicad_sch(
);

    wire w1;
    wire w2;
    wire w3;
    wire w4;
    wire w5;
    wire w6;
    wire w7;

    GND #PWR0102(/* */);
    +5V #PWR0101(/* */);
    LED D1(/* */);
    DGOF5S3 X1(/* */);
    GND #PWR0103(/* */);
    GND #PWR0104(/* */);
    LED D2(/* */);
    TestIC_kicad_sch TestIC(/* */);
endmodule
