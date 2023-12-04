const riscvDocumentation = html` <div class="container-fluid">
    <h2 id="instructions">Instructions</h2>
    <p>
        This simulator supports a subset of the RISC-V32 ISA. The supported
        instructions are listed below.
    </p>
    <h3 id="r-type">R-Type</h3>
    <div class="table-responsive">
        <table class="table table-bordered table-hover table-instr-op">
            <thead>
                <tr>
                    <th>Instruction</th>
                    <th>Operation</th>
                    <th>Notes</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>
                        <code>ADD rd, rs1, rs2</code>
                    </td>
                    <td>
                        <code>rd = rs1 + rs2</code>
                    </td>
                    <td></td>
                </tr>
                <tr>
                    <td>
                        <code>SUB rd, rs1, rs2</code>
                    </td>
                    <td>
                        <code>rd = rs1 - rs2</code>
                    </td>
                    <td></td>
                </tr>
                <tr>
                    <td>
                        <code>SLL rd, rs1, rs2</code>
                    </td>
                    <td>
                        <code>rd = rs1 &lt;&lt; rs2</code>
                    </td>
                    <td></td>
                </tr>
                <tr>
                    <td>
                        <code>SRL rd, rs1, rs2</code>
                    </td>
                    <td>
                        <code>rd = rs1 &gt;&gt; rs2</code>
                    </td>
                    <td>Logical right shift</td>
                </tr>
                <tr>
                    <td>
                        <code>SRA rd, rs1, rs2</code>
                    </td>
                    <td>
                        <code>rd = rs1 &gt;&gt;a rs2</code>
                    </td>
                    <td>Arithmetic right shift</td>
                </tr>
                <tr>
                    <td>
                        <code>SLT rd, rs1, rs2</code>
                    </td>
                    <td>
                        <code>rd = rs1 &lt;s rs2</code>
                    </td>
                    <td>
                        Set <code>rd</code> to 1 if the value in
                        <code>rs1</code> is less than the value in
                        <code>rs2</code>, otherwise 0 (both values are treated
                        as signed)
                    </td>
                </tr>
                <tr>
                    <td>
                        <code>SLTU rd, rs1, rs2</code>
                    </td>
                    <td>
                        <code>rd = rs1 &lt;u rs2</code>
                    </td>
                    <td>
                        Set <code>rd</code> to 1 if the value in
                        <code>rs1</code> is less than the value in
                        <code>rs2</code>, otherwise 0 (both values are treated
                        as unsigned)
                    </td>
                </tr>
                <tr>
                    <td>
                        <code>AND rd, rs1, rs2</code>
                    </td>
                    <td>
                        <code>rd = rs1 &amp; rs2</code>
                    </td>
                    <td></td>
                </tr>
                <tr>
                    <td>
                        <code>OR rd, rs1, rs2</code>
                    </td>
                    <td>
                        <code>rd = rs1 | rs2</code>
                    </td>
                    <td></td>
                </tr>
                <tr>
                    <td>
                        <code>XOR rd, rs1, rs2</code>
                    </td>
                    <td>
                        <code>rd = rs1 ^ rs2</code>
                    </td>
                    <td></td>
                </tr>
            </tbody>
        </table>
    </div>

    <h3 id="i-type">I-Type</h3>
    <p>
        Unless otherwise specified, the immediate (<code>imm</code>) has a
        length of 12 bits and is sign extended to 32 bits.
        <br />
        <code>var</code> is a variable name, <code>index</code> is an optional
        array index.
    </p>
    <div class="table-responsive">
        <table class="table table-bordered table-hover table-instr-op">
            <thead>
                <tr>
                    <th>Instruction</th>
                    <th>Operation</th>
                    <th>Notes</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>
                        <code>ADDI rd, rs1, imm</code>
                    </td>
                    <td>
                        <code>rd = rs1 + imm</code>
                    </td>
                    <td></td>
                </tr>
                <tr>
                    <td>
                        <code>SLTI rd, rs1, imm</code>
                    </td>
                    <td>
                        <code>rd = rs1 &lt;s imm</code>
                    </td>
                    <td>
                        Set <code>rd</code> to 1 if the value in
                        <code>rs1</code> is less than the value in
                        <code>imm</code>, otherwise 0 (both values are treated
                        as signed)
                    </td>
                </tr>
                <tr>
                    <td>
                        <code>SLTIU rd, rs1, imm</code>
                    </td>
                    <td>
                        <code>rd = rs1 &lt;u imm</code>
                    </td>
                    <td>
                        Set <code>rd</code> to 1 if the value in
                        <code>rs1</code> is less than the value in
                        <code>imm</code>, otherwise 0 (both values are treated
                        as unsigned)
                    </td>
                </tr>
                <tr>
                    <td>
                        <code>ANDI rd, rs1, imm</code>
                    </td>
                    <td>
                        <code>rd = rs1 &amp; imm</code>
                    </td>
                    <td></td>
                </tr>
                <tr>
                    <td>
                        <code>ORI rd, rs1, imm</code>
                    </td>
                    <td>
                        <code>rd = rs1 | imm</code>
                    </td>
                    <td></td>
                </tr>
                <tr>
                    <td>
                        <code>XORI rd, rs1, imm</code>
                    </td>
                    <td>
                        <code>rd = rs1 ^ imm</code>
                    </td>
                    <td></td>
                </tr>
                <tr>
                    <td>
                        <code>SLLI rd, rs1, imm</code>
                    </td>
                    <td>
                        <code>rd = rs1 &lt;&lt; imm</code>
                    </td>
                    <td>
                        <code>imm</code> is unsigned, with a length of 5 bits
                    </td>
                </tr>
                <tr>
                    <td>
                        <code>SRLI rd, rs1, imm</code>
                    </td>
                    <td>
                        <code>rd = rs1 &gt;&gt; imm</code>
                    </td>
                    <td>
                        Logical right shift.<br /><code>imm</code>
                        is unsigned, with a length of 5 bits
                    </td>
                </tr>
                <tr>
                    <td>
                        <code>SRAI rd, rs1, imm</code>
                    </td>
                    <td>
                        <code>rd = rs1 &gt;&gt;a imm</code>
                    </td>
                    <td>
                        Arithmetic right shift.<br /><code>imm</code>
                        is unsigned, with a length of 5 bits
                    </td>
                </tr>
                <tr>
                    <td>
                        <code
                            >LB rd, rs1, imm<br />
                            LB rd, imm(rs1)<br />
                            LB rd, var[index]</code
                        >
                    </td>
                    <td>
                        <code
                            >rd = M[rs1 + imm]<br />
                            rd = var[index]</code
                        >
                    </td>
                    <td>
                        Load byte.<br /><code>rd</code>
                        is sign extended to 32 bits
                    </td>
                </tr>
                <tr>
                    <td>
                        <code
                            >LH rd, rs1, imm<br />
                            LH rd, imm(rs1)<br />
                            LH rd, var[index]</code
                        >
                    </td>
                    <td>
                        <code
                            >rd = M[rs1 + imm]<br />
                            rd = var[index]</code
                        >
                    </td>
                    <td>
                        Load two bytes.<br /><code>rd</code>
                        is sign extended to 32 bits
                    </td>
                </tr>
                <tr>
                    <td>
                        <code
                            >LW rd, rs1, imm<br />
                            LW rd, imm(rs1)<br />
                            LW rd, var[index]</code
                        >
                    </td>
                    <td>
                        <code
                            >rd = M[rs1 + imm]<br />
                            rd = var[index]</code
                        >
                    </td>
                    <td>
                        Load four bytes.<br /><code>rd</code>
                        is sign extended to 32 bits
                    </td>
                </tr>
                <tr>
                    <td>
                        <code
                            >LBU rd, rs1, imm<br />
                            LBU rd, imm(rs1)<br />
                            LBU rd, var[index]</code
                        >
                    </td>
                    <td>
                        <code
                            >rd = M[rs1 + imm]<br />
                            rd = var[index]</code
                        >
                    </td>
                    <td>Load byte</td>
                </tr>
                <tr>
                    <td>
                        <code
                            >LHU rd, rs1, imm<br />
                            LHU rd, imm(rs1)<br />
                            LHU rd, var[index]</code
                        >
                    </td>
                    <td>
                        <code
                            >rd = M[rs1 + imm]<br />
                            rd = var[index]</code
                        >
                    </td>
                    <td>Load two bytes</td>
                </tr>
                <tr>
                    <td>
                        <code>JALR rd, rs1, imm</code>
                    </td>
                    <td>
                        <code>rd = PC + 4; PC = rs1 + imm</code>
                    </td>
                    <td>
                        Jump and link register.
                        <code>rd</code> is set to the address of the instruction
                        following the jump. The jump target is
                        <code>rs1 + imm</code>
                        with the least significant bit cleared.
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <h3 id="s-type">S-Type</h3>
    <p>
        The immediate (<code>imm</code>) has a length of 12 bits and is sign
        extended to 32 bits. <br />
        <code>var</code> is a variable name, <code>index</code> is an optional
        array index.
    </p>
    <div class="table-responsive">
        <table class="table table-bordered table-hover table-instr-op">
            <thead>
                <tr>
                    <th>Instruction</th>
                    <th>Operation</th>
                    <th>Notes</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>
                        <code
                            >SB rs1, rs2, imm<br />
                            SB rs1, imm(rs2)<br />
                            SB rs1, var[index], rs2</code
                        >
                    </td>
                    <td>
                        <code
                            >M[rs2 + imm] = rs1<br />
                            var[index] = rs1</code
                        >
                    </td>
                    <td>
                        Store byte.<br />If a variable is modified,
                        <code>rs2</code> is used as a temporary register, that
                        will be overwritten.
                    </td>
                </tr>
                <tr>
                    <td>
                        <code
                            >SH rs1, rs2, imm<br />
                            SH rs1, imm(rs2)<br />
                            SH rs1, var[index], rs2</code
                        >
                    </td>
                    <td>
                        <code
                            >M[rs2 + imm] = rs1<br />
                            var[index] = rs1</code
                        >
                    </td>
                    <td>
                        Store two bytes.<br />If a variable is modified,
                        <code>rs2</code> is used as a temporary register, that
                        will be overwritten.
                    </td>
                </tr>
                <tr>
                    <td>
                        <code
                            >SW rs1, rs2, imm<br />
                            SW rs1, imm(rs2)<br />
                            SW rs1, var[index], rs2</code
                        >
                    </td>
                    <td>
                        <code
                            >M[rs2 + imm] = rs1<br />
                            var[index] = rs1</code
                        >
                    </td>
                    <td>
                        Store four bytes.<br />If a variable is modified,
                        <code>rs2</code> is used as a temporary register, that
                        will be overwritten.
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    <h3 id="b-type">B-Type</h3>
    <p>
        The immediate (<code>imm</code>) has a length of 13 bits and is sign
        extended to 32 bits. <br />
        Offsets are optional, and in hexadecimal format.
    </p>
    <div class="table-responsive">
        <table class="table table-bordered table-hover table-instr-op">
            <thead>
                <tr>
                    <th>Instruction</th>
                    <th>Operation</th>
                    <th>Notes</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>
                        <code
                            >BEQ rs1, rs2, imm<br />
                            BEQ rs1, rs2, label+offset</code
                        >
                    </td>
                    <td>
                        <code>if (rs1 == rs2) PC = PC + imm</code>
                    </td>
                    <td>Branch if equal</td>
                </tr>
                <tr>
                    <td>
                        <code
                            >BNE rs1, rs2, imm<br />
                            BNE rs1, rs2, label+offset</code
                        >
                    </td>
                    <td>
                        <code>if (rs1 != rs2) PC = PC + imm</code>
                    </td>
                    <td>Branch if not equal</td>
                </tr>
                <tr>
                    <td>
                        <code
                            >BLT rs1, rs2, imm<br />
                            BLT rs1, rs2, label+offset</code
                        >
                    </td>
                    <td>
                        <code>if (rs1 &lt;s rs2) PC = PC + imm</code>
                    </td>
                    <td>Branch if less than</td>
                </tr>
                <tr>
                    <td>
                        <code
                            >BGE rs1, rs2, imm<br />
                            BGE rs1, rs2, label+offset</code
                        >
                    </td>
                    <td>
                        <code>if (rs1 &gt;=s rs2) PC = PC + imm</code>
                    </td>
                    <td>Branch if greater than or equal</td>
                </tr>
                <tr>
                    <td>
                        <code
                            >BLTU rs1, rs2, imm<br />
                            BLTU rs1, rs2, label+offset</code
                        >
                    </td>
                    <td>
                        <code>if (rs1 &lt;u rs2) PC = PC + imm</code>
                    </td>
                    <td>Branch if less than (unsigned)</td>
                </tr>
                <tr>
                    <td>
                        <code
                            >BGEU rs1, rs2, imm<br />
                            BGEU rs1, rs2, label+offset</code
                        >
                    </td>
                    <td>
                        <code>if (rs1 &gt;=u rs2) PC = PC + imm</code>
                    </td>
                    <td>Branch if greater than or equal (unsigned)</td>
                </tr>
            </tbody>
        </table>
    </div>

    <h3 id="u-type">U-Type</h3>
    <p>
        The immediate (<code>imm</code>) has a length of 20 bits and is sign
        extended to 32 bits.
    </p>
    <div class="table-responsive">
        <table class="table table-bordered table-hover table-instr-op">
            <thead>
                <tr>
                    <th>Instruction</th>
                    <th>Operation</th>
                    <th>Notes</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>
                        <code>LUI rd, imm</code>
                    </td>
                    <td>
                        <code>rd = imm &lt;&lt; 12</code>
                    </td>
                    <td></td>
                </tr>
                <tr>
                    <td>
                        <code>AUIPC rd, imm</code>
                    </td>
                    <td>
                        <code>rd = PC + (imm &lt;&lt; 12)</code>
                    </td>
                    <td></td>
                </tr>
            </tbody>
        </table>
    </div>

    <h3 id="j-type">J-Type</h3>
    <p>
        The immediate (<code>imm</code>) has a length of 21 bits and is sign
        extended to 32 bits.<br />
        Offsets are optional, and in hexadecimal format.
    </p>
    <div class="table-responsive">
        <table class="table table-bordered table-hover table-instr-op">
            <thead>
                <tr>
                    <th>Instruction</th>
                    <th>Operation</th>
                    <th>Notes</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>
                        <code
                            >JAL rd, imm<br />
                            JAL rd, label+offset</code
                        >
                    </td>
                    <td>
                        <code>rd = PC + 4; PC = PC + imm</code>
                    </td>
                    <td>
                        Jump and link.
                        <code>rd</code> is set to the address of the instruction
                        following the jump.
                    </td>
                </tr>
            </tbody>
        </table>

        <h3 id="csr-type">CSR-Type</h3>
        <p>
            <i>Currently not implemented in 5-stage pipeline mode.</i> <br />
            The unsigned immediate (<code>uimm</code>) has a length of 5 bits.
        </p>
        <div class="table-responsive">
            <table class="table table-bordered table-hover table-instr-op">
                <thead>
                    <tr>
                        <th>Instruction</th>
                        <th>Operation</th>
                        <th>Notes</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>
                            <code>CSRRW rd, csr, rs1</code>
                        </td>
                        <td>
                            <code>rd = csr; csr = rs1</code>
                        </td>
                        <td>Atomic read/write</td>
                    </tr>
                    <tr>
                        <td>
                            <code>CSRRS rd, csr, rs1</code>
                        </td>
                        <td>
                            <code>rd = csr; csr = csr | rs1</code>
                        </td>
                        <td>
                            Atomic read/set.
                            <code>rs1</code>
                            serves as a bit mask
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <code>CSRRC rd, csr, rs1</code>
                        </td>
                        <td>
                            <code>rd = csr; csr = csr &amp; ~rs1</code>
                        </td>
                        <td>
                            Atomic read/clear.
                            <code>rs1</code>
                            serves as a bit mask
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <code>CSRRWI rd, csr, uimm</code>
                        </td>
                        <td>
                            <code>rd = csr; csr = uimm</code>
                        </td>
                        <td>Atomic read/write</td>
                    </tr>
                    <tr>
                        <td>
                            <code>CSRRSI rd, csr, uimm</code>
                        </td>
                        <td>
                            <code>rd = csr; csr = csr | uimm</code>
                        </td>
                        <td>
                            Atomic read/set.
                            <code>uimm</code>
                            serves as a bit mask
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <code>CSRRCI rd, csr, uimm</code>
                        </td>
                        <td>
                            <code>rd = csr; csr = csr &amp; ~uimm</code>
                        </td>
                        <td>
                            Atomic read/clear.
                            <code>uimm</code>
                            serves as a bit mask
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <h3 id="pseudoinstructions">Pseudoinstructions</h3>
        <p>
            <code>var</code> is a variable name, <code>index</code> is an
            optional array index.
        </p>
        <div class="table-responsive">
            <table class="table table-bordered table-hover table-instr-op">
                <thead>
                    <tr>
                        <th>Instruction</th>
                        <th>Operation</th>
                        <th>Notes</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>
                            <code>NOP</code>
                        </td>
                        <td><code>-</code></td>
                        <td>
                            No operation. Translated to
                            <code>ADDI x0, x0, 0</code>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <code>LA rd, var[index]</code>
                        </td>
                        <td>
                            <code>rd = &var[index]</code>
                        </td>
                        <td>
                            Load variable address into
                            <code>rd</code>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <code>LI rd, imm</code>
                        </td>
                        <td>
                            <code>rd = imm</code>
                        </td>
                        <td>
                            Load 32 bit immediate into
                            <code>rd</code>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <h3 id="misc">Miscellaneous</h3>
        <div class="table-responsive">
            <table class="table table-bordered table-hover table-instr-op">
                <thead>
                    <tr>
                        <th>Instruction</th>
                        <th>Operation</th>
                        <th>Notes</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>
                            <code>ECALL</code>
                        </td>
                        <td><code>-</code></td>
                        <td>Recognized but currently not implemented</td>
                    </tr>
                    <tr>
                        <td>
                            <code>EBREAK</code>
                        </td>
                        <td><code>-</code></td>
                        <td>Recognized but currently not implemented</td>
                    </tr>
                    <tr>
                        <td>
                            <code>FENCE rd, rs1</code>
                        </td>
                        <td><code>-</code></td>
                        <td>Recognized but currently not implemented</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <h2 id="labels">Comments and labels</h2>
    <p>
        Comments can be added to the code using
        <code>#</code>.<br />
        Labels are added by appending a colon
        <code>:</code> to a label name. They can be used as jump targets.
    </p>
    <pre class="bg-light">
# This is a comment
my_label:
addi x1, x1, 1
jal x2, my_label
addi x3, x3, 1 # This line is never reached</pre
    >

    <h2 id="variables">Segments and variables</h2>
    <p>
        In addition to the program code, the simulator supports a data segment.
        It can be used to store variables and arrays in the simulator's memory.
    </p>
    <p>
        In order to define a data segment, the
        <code>.data</code> directive is used, while the
        <code>.text</code> directive designates the code segment.
    </p>
    <p>
        The following example demonstrates how to declare and use variables and
        arrays, employing all currently supported data types:
    </p>
    <pre class="bg-light">
.data
    my_var1: .byte -128
    my_var2: .half 0x1234, 0b1010, 999
    my_var3: .word 0x12345678, 0b111
    text1:   .string "Hello, World!"  # ASCII byte array
.text
    la x1, my_var1     # load address of my_var1 into x1
    lh x2, my_var2     # load halfword from my_var2 into x2
    lh x3, my_var2[0]  # same effect as above
    lh x4, my_var2[2]  # x4 = 999
    lw x5, my_var3[1]  # x5 = 0b111
    lb x6, text1[11]   # x6 = '!'</pre
    >
    <p>
        If no directives are given, the entire input is interpreted as code.<br />
        Similarly, if a <code>.data</code> but no <code>.text</code> directive
        is given, every line before the data segment is interpreted as code.
        <br />
        There is no fixed segmentation order. However, declaring multiple
        segments of the same type will throw an error.
    </p>
</div>`;
