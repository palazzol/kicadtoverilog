module NOR2(
    output Y,
    input A,
    input B);

    assign Y = !(A|B);
endmodule

module AND2(
    output Y,
    input A,
    input B);

    assign Y = A&B;
endmodule

module NOT(
    output Y,
    input A);

    assign Y = !A;
endmodule
