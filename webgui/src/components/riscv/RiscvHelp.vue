<!-- The riscv help page content. -->
<template>
    <div class="container-fluid">
        <h1>RISC-V</h1>
        <h2 id="instructions">Instructions</h2>
        <p>
            This simulator supports a subset of the RISC-V32 ISA. The supported
            instructions are listed below.
        </p>
        <!--my_acc_marker-->
        <div class="accordion" id="accordionPanelsStayOpenExample">
            <div class="accordion-item">
                <h3 class="accordion-header" id="panelsStayOpen-headingOne">
                    <button
                        class="accordion-button collapsed"
                        type="button"
                        data-bs-toggle="collapse"
                        data-bs-target="#panelsStayOpen-collapseOne"
                        aria-expanded="false"
                        aria-controls="panelsStayOpen-collapseOne"
                    >
                        R-Type
                    </button>
                </h3>
                <div
                    id="panelsStayOpen-collapseOne"
                    class="accordion-collapse collapse"
                    aria-labelledby="panelsStayOpen-headingOne"
                >
                    <div class="accordion-body">
                        <div class="table-responsive">
                            <table
                                class="table table-bordered table-hover table-instr-op"
                            >
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
                                            Set <code>rd</code> to 1 if the
                                            value in <code>rs1</code> is less
                                            than the value in <code>rs2</code>,
                                            otherwise 0 (both values are treated
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
                                            Set <code>rd</code> to 1 if the
                                            value in <code>rs1</code> is less
                                            than the value in <code>rs2</code>,
                                            otherwise 0 (both values are treated
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
                                    <tr>
                                        <td>
                                            <code>MUL rd, rs1, rs2</code>
                                        </td>
                                        <td>
                                            <code>rd = rs1 * rs2</code>
                                        </td>
                                        <td>
                                            (M), places the lower 32 bits of the
                                            result in the destination register
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <code>MULH rd, rs1, rs2</code>
                                        </td>
                                        <td>
                                            <code>rd = rs1 s*s rs2</code>
                                        </td>
                                        <td>
                                            (M), places the upper 32 bits of the
                                            result in the destination register,
                                            both rs1 and rs2 are treated as
                                            signed
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <code>MULHU rd, rs1, rs2</code>
                                        </td>
                                        <td>
                                            <code>rd = rs1 u*u rs2</code>
                                        </td>
                                        <td>
                                            (M), places the upper 32 bits of the
                                            result in the destination register,
                                            both rs1 and rs2 are treated as
                                            unsigned
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <code>MULHSU rd, rs1, rs2</code>
                                        </td>
                                        <td>
                                            <code>rd = rs1 s*u rs2</code>
                                        </td>
                                        <td>
                                            (M), places the upper 32 bits of the
                                            result in the destination register,
                                            rs1 treated as signed, rs2 treated
                                            as unsigned
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <code>DIV rd, rs1, rs2</code>
                                        </td>
                                        <td>
                                            <code>rd = rs1 /s rs2</code>
                                        </td>
                                        <td>(M), signed integer division</td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <code>DIVU rd, rs1, rs2</code>
                                        </td>
                                        <td>
                                            <code>rd = rs1 /u rs2</code>
                                        </td>
                                        <td>(M), unsigned integer division</td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <code>REM rd, rs1, rs2</code>
                                        </td>
                                        <td>
                                            <code>rd = rs1 %s rs2</code>
                                        </td>
                                        <td>
                                            (M), remainder of signed integer
                                            division
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <code>REMU rd, rs1, rs2</code>
                                        </td>
                                        <td>
                                            <code>rd = rs1 %u rs2</code>
                                        </td>
                                        <td>
                                            (M), remainder of unsigned integer
                                            division
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <p>
                            Note: Instructions marked with (M) are part of the
                            "M" Standard Extension for Integer Multiplication
                            and Division.
                        </p>
                    </div>
                </div>
            </div>
            <div class="accordion-item">
                <h3 class="accordion-header" id="panelsStayOpen-headingTwo">
                    <button
                        class="accordion-button collapsed"
                        type="button"
                        data-bs-toggle="collapse"
                        data-bs-target="#panelsStayOpen-collapseTwo"
                        aria-expanded="false"
                        aria-controls="panelsStayOpen-collapseTwo"
                    >
                        I-Type
                    </button>
                </h3>
                <div
                    id="panelsStayOpen-collapseTwo"
                    class="accordion-collapse collapse"
                    aria-labelledby="panelsStayOpen-headingTwo"
                >
                    <div class="accordion-body">
                        <p>
                            Unless otherwise specified, the immediate
                            (<code>imm</code>) has a length of 12 bits and is
                            sign extended to 32 bits.
                            <br />
                            <code>var</code> is a variable name,
                            <code>index</code> is an optional array index.
                        </p>
                        <div class="table-responsive">
                            <table
                                class="table table-bordered table-hover table-instr-op"
                            >
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
                                            Set <code>rd</code> to 1 if the
                                            value in <code>rs1</code> is less
                                            than the value in <code>imm</code>,
                                            otherwise 0 (both values are treated
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
                                            Set <code>rd</code> to 1 if the
                                            value in <code>rs1</code> is less
                                            than the value in <code>imm</code>,
                                            otherwise 0 (both values are treated
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
                                            <code>imm</code> is unsigned, with a
                                            length of 5 bits
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
                                            Logical right shift.<br /><code
                                                >imm</code
                                            >
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
                                            Arithmetic right shift.<br /><code
                                                >imm</code
                                            >
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
                                            Load four bytes.<br /><code
                                                >rd</code
                                            >
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
                                            <code
                                                >rd = PC + 4; PC = rs1 +
                                                imm</code
                                            >
                                        </td>
                                        <td>
                                            Jump and link register.
                                            <code>rd</code> is set to the
                                            address of the instruction following
                                            the jump. The jump target is
                                            <code>rs1 + imm</code>
                                            with the least significant bit
                                            cleared.
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <code>ECALL</code>
                                        </td>
                                        <td>
                                            <code>environment call</code>
                                        </td>
                                        <td>
                                            See section
                                            <a href="#riscv-help-ecalls"
                                                >ECALLs</a
                                            >.
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            <div class="accordion-item">
                <h3 class="accordion-header" id="panelsStayOpen-headingThree">
                    <button
                        class="accordion-button collapsed"
                        type="button"
                        data-bs-toggle="collapse"
                        data-bs-target="#panelsStayOpen-collapseThree"
                        aria-expanded="false"
                        aria-controls="panelsStayOpen-collapseThree"
                    >
                        S-Type
                    </button>
                </h3>
                <div
                    id="panelsStayOpen-collapseThree"
                    class="accordion-collapse collapse"
                    aria-labelledby="panelsStayOpen-headingThree"
                >
                    <div class="accordion-body">
                        <p>
                            The immediate (<code>imm</code>) has a length of 12
                            bits and is sign extended to 32 bits. <br />
                            <code>var</code> is a variable name,
                            <code>index</code> is an optional array index.
                        </p>
                        <div class="table-responsive">
                            <table
                                class="table table-bordered table-hover table-instr-op"
                            >
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
                                            Store byte.<br />If a variable is
                                            modified, <code>rs2</code> is used
                                            as a temporary register, that will
                                            be overwritten.
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
                                            Store two bytes.<br />If a variable
                                            is modified, <code>rs2</code> is
                                            used as a temporary register, that
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
                                            Store four bytes.<br />If a variable
                                            is modified, <code>rs2</code> is
                                            used as a temporary register, that
                                            will be overwritten.
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            <div class="accordion-item">
                <h3 class="accordion-header" id="panelsStayOpen-headingFour">
                    <button
                        class="accordion-button collapsed"
                        type="button"
                        data-bs-toggle="collapse"
                        data-bs-target="#panelsStayOpen-collapseFour"
                        aria-expanded="false"
                        aria-controls="panelsStayOpen-collapseFour"
                    >
                        B-Type
                    </button>
                </h3>
                <div
                    id="panelsStayOpen-collapseFour"
                    class="accordion-collapse collapse"
                    aria-labelledby="panelsStayOpen-headingFour"
                >
                    <div class="accordion-body">
                        <p>
                            The immediate (<code>imm</code>) has a length of 13
                            bits and is sign extended to 32 bits. <br />
                            Offsets are optional, and in hexadecimal format.
                        </p>
                        <div class="table-responsive">
                            <table
                                class="table table-bordered table-hover table-instr-op"
                            >
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
                                            <code
                                                >if (rs1 == rs2) PC = PC +
                                                imm</code
                                            >
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
                                            <code
                                                >if (rs1 != rs2) PC = PC +
                                                imm</code
                                            >
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
                                            <code
                                                >if (rs1 &lt;s rs2) PC = PC +
                                                imm</code
                                            >
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
                                            <code
                                                >if (rs1 &gt;=s rs2) PC = PC +
                                                imm</code
                                            >
                                        </td>
                                        <td>Branch if greater than or equal</td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <code
                                                >BLTU rs1, rs2, imm<br />
                                                BLTU rs1, rs2,
                                                label+offset</code
                                            >
                                        </td>
                                        <td>
                                            <code
                                                >if (rs1 &lt;u rs2) PC = PC +
                                                imm</code
                                            >
                                        </td>
                                        <td>Branch if less than (unsigned)</td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <code
                                                >BGEU rs1, rs2, imm<br />
                                                BGEU rs1, rs2,
                                                label+offset</code
                                            >
                                        </td>
                                        <td>
                                            <code
                                                >if (rs1 &gt;=u rs2) PC = PC +
                                                imm</code
                                            >
                                        </td>
                                        <td>
                                            Branch if greater than or equal
                                            (unsigned)
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            <div class="accordion-item">
                <h3 class="accordion-header" id="panelsStayOpen-headingFive">
                    <button
                        class="accordion-button collapsed"
                        type="button"
                        data-bs-toggle="collapse"
                        data-bs-target="#panelsStayOpen-collapseFive"
                        aria-expanded="false"
                        aria-controls="panelsStayOpen-collapseFive"
                    >
                        U-Type
                    </button>
                </h3>
                <div
                    id="panelsStayOpen-collapseFive"
                    class="accordion-collapse collapse"
                    aria-labelledby="panelsStayOpen-headingFive"
                >
                    <div class="accordion-body">
                        <p>
                            The immediate (<code>imm</code>) has a length of 20
                            bits and is sign extended to 32 bits.
                        </p>
                        <div class="table-responsive">
                            <table
                                class="table table-bordered table-hover table-instr-op"
                            >
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
                                            <code
                                                >rd = PC + (imm &lt;&lt;
                                                12)</code
                                            >
                                        </td>
                                        <td></td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            <div class="accordion-item">
                <h3 class="accordion-header" id="panelsStayOpen-headingSix">
                    <button
                        class="accordion-button collapsed"
                        type="button"
                        data-bs-toggle="collapse"
                        data-bs-target="#panelsStayOpen-collapseSix"
                        aria-expanded="false"
                        aria-controls="panelsStayOpen-collapseSix"
                    >
                        J-Type
                    </button>
                </h3>
                <div
                    id="panelsStayOpen-collapseSix"
                    class="accordion-collapse collapse"
                    aria-labelledby="panelsStayOpen-headingSix"
                >
                    <div class="accordion-body">
                        <p>
                            The address to jump to (<code>addr</code>), is
                            encoded relative to the current pc in a 21 bit
                            immediate that is sign extended to 32 bits and added
                            to the current pc.<br />
                            Offsets are optional, and in hexadecimal format.
                        </p>
                        <div class="table-responsive">
                            <table
                                class="table table-bordered table-hover table-instr-op"
                            >
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
                                                >JAL rd, addr<br />
                                                JAL rd, label+offset</code
                                            >
                                        </td>
                                        <td>
                                            <code>rd = PC + 4; PC = addr</code>
                                        </td>
                                        <td>
                                            Jump and link.
                                            <code>rd</code> is set to the
                                            address of the instruction following
                                            the jump.
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            <div class="accordion-item">
                <h3 class="accordion-header" id="panelsStayOpen-headingSeven">
                    <button
                        class="accordion-button collapsed"
                        type="button"
                        data-bs-toggle="collapse"
                        data-bs-target="#panelsStayOpen-collapseSeven"
                        aria-expanded="false"
                        aria-controls="panelsStayOpen-collapseSeven"
                    >
                        CSR-Type
                    </button>
                </h3>
                <div
                    id="panelsStayOpen-collapseSeven"
                    class="accordion-collapse collapse"
                    aria-labelledby="panelsStayOpen-headingSeven"
                >
                    <div class="accordion-body">
                        <p>
                            <i
                                >Currently not implemented in 5-stage pipeline
                                mode.</i
                            >
                            <br />
                            The unsigned immediate (<code>uimm</code>) has a
                            length of 5 bits.
                        </p>
                        <div class="table-responsive">
                            <table
                                class="table table-bordered table-hover table-instr-op"
                            >
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
                                            <code
                                                >rd = csr; csr = csr | rs1</code
                                            >
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
                                            <code
                                                >rd = csr; csr = csr &amp;
                                                ~rs1</code
                                            >
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
                                            <code
                                                >rd = csr; csr = csr |
                                                uimm</code
                                            >
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
                                            <code
                                                >rd = csr; csr = csr &amp;
                                                ~uimm</code
                                            >
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
                    </div>
                </div>
            </div>
            <div class="accordion-item">
                <h3 class="accordion-header" id="panelsStayOpen-headingEight">
                    <button
                        class="accordion-button collapsed"
                        type="button"
                        data-bs-toggle="collapse"
                        data-bs-target="#panelsStayOpen-collapseEight"
                        aria-expanded="false"
                        aria-controls="panelsStayOpen-collapseEight"
                    >
                        Pseudoinstructions
                    </button>
                </h3>
                <div
                    id="panelsStayOpen-collapseEight"
                    class="accordion-collapse collapse"
                    aria-labelledby="panelsStayOpen-headingEight"
                >
                    <div class="accordion-body">
                        <p>
                            <code>var</code> is a variable name,
                            <code>index</code> is an optional array index.
                        </p>
                        <div class="table-responsive">
                            <table
                                class="table table-bordered table-hover table-instr-op"
                            >
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
                                    <tr>
                                        <td>
                                            <code>MV rd, rs</code>
                                        </td>
                                        <td><code>rd = rs</code></td>
                                        <td>
                                            Translated to
                                            <code>ADDI rd, rs, 0</code>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            <div class="accordion-item">
                <h3 class="accordion-header" id="panelsStayOpen-headingNine">
                    <button
                        class="accordion-button collapsed"
                        type="button"
                        data-bs-toggle="collapse"
                        data-bs-target="#panelsStayOpen-collapseNine"
                        aria-expanded="false"
                        aria-controls="panelsStayOpen-collapseNine"
                    >
                        Miscellaneous
                    </button>
                </h3>
                <div
                    id="panelsStayOpen-collapseNine"
                    class="accordion-collapse collapse"
                    aria-labelledby="panelsStayOpen-headingNine"
                >
                    <div class="accordion-body">
                        <div class="table-responsive">
                            <table
                                class="table table-bordered table-hover table-instr-op"
                            >
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
                                            <code>EBREAK</code>
                                        </td>
                                        <td><code>-</code></td>
                                        <td>
                                            Recognized but currently not
                                            implemented
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <code>FENCE rd, rs1</code>
                                        </td>
                                        <td><code>-</code></td>
                                        <td>
                                            Recognized but currently not
                                            implemented
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <!--my_acc_marker-->
        <h2 id="instructions">Other</h2>
        <!--my_acc_marker-->
        <div class="accordion" id="accordionPanelsStayOpenExample">
            <div class="accordion-item">
                <h3 class="accordion-header" id="panelsStayOpen-headingTen">
                    <button
                        class="accordion-button collapsed"
                        type="button"
                        data-bs-toggle="collapse"
                        data-bs-target="#panelsStayOpen-collapseTen"
                        aria-expanded="false"
                        aria-controls="panelsStayOpen-collapseTen"
                    >
                        Comments and labels
                    </button>
                </h3>
                <div
                    id="panelsStayOpen-collapseTen"
                    class="accordion-collapse collapse"
                    aria-labelledby="panelsStayOpen-headingTen"
                >
                    <div class="accordion-body">
                        <p>
                            Comments can be added to the code using
                            <code>#</code>.<br />
                            Labels are added by appending a colon
                            <code>:</code> to a label name. They can be used as
                            jump targets.
                        </p>
                        <pre class="bg-light">
# This is a comment
my_label:
addi x1, x1, 1
jal x2, my_label
addi x3, x3, 1 # This line is never reached</pre
                        >
                    </div>
                </div>
            </div>
            <div class="accordion-item">
                <h3 class="accordion-header" id="panelsStayOpen-headingEleven">
                    <button
                        class="accordion-button collapsed"
                        type="button"
                        data-bs-toggle="collapse"
                        data-bs-target="#panelsStayOpen-collapseEleven"
                        aria-expanded="false"
                        aria-controls="panelsStayOpen-collapseEleven"
                    >
                        Segments and variables
                    </button>
                </h3>
                <div
                    id="panelsStayOpen-collapseEleven"
                    class="accordion-collapse collapse"
                    aria-labelledby="panelsStayOpen-headingEleven"
                >
                    <div class="accordion-body">
                        <p>
                            In addition to the program code, the simulator
                            supports a data segment. It can be used to store
                            variables and arrays in the simulator's memory.
                        </p>
                        <p>
                            In order to define a data segment, the
                            <code>.data</code> directive is used, while the
                            <code>.text</code> directive designates the code
                            segment.
                        </p>
                        <p>
                            The following example demonstrates how to declare
                            and use variables and arrays, employing all
                            currently supported data types. Note that all
                            variables/arrays are word-aligned (addresses are
                            multiples of 4), which is achieved by zero-padding
                            preceding variables.
                        </p>
                        <pre class="bg-light">
.data
    empty_array: .zero 64 # reserves space for 64 words (256 bytes)
    # The following two declarations of 'my_var1' are equivalent,
    # since zero padding is used to ensure word alignment of new variables/arrays.
    my_var1: .byte -128
    # my_var1: .byte -128, 0, 0, 0
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
                            If no directives are given, the entire input is
                            interpreted as code.<br />
                            Similarly, if a <code>.data</code> but no
                            <code>.text</code> directive is given, every line
                            before the data segment is interpreted as code.
                            <br />
                            There is no fixed segmentation order. However,
                            declaring multiple segments of the same type will
                            throw an error.
                        </p>
                    </div>
                </div>
            </div>
            <div class="accordion-item">
                <h3 class="accordion-header" id="panelsStayOpen-headingTwelve">
                    <button
                        class="accordion-button collapsed"
                        type="button"
                        data-bs-toggle="collapse"
                        data-bs-target="#panelsStayOpen-collapseTwelve"
                        aria-expanded="false"
                        aria-controls="panelsStayOpen-collapseTwelve"
                    >
                        Cache Simulation
                    </button>
                </h3>
                <div
                    id="panelsStayOpen-collapseTwelve"
                    class="accordion-collapse collapse"
                    aria-labelledby="panelsStayOpen-headingTwelve"
                >
                    <div class="accordion-body">
                        <p>
                            You can activate separate caches for data and
                            instructions in the settings. These caches can be
                            configured as Write-through with Write no-allocate
                            or Write-back with Write allocate. The number of
                            sets, block size and associativity are also
                            configurable. You can also choose between LRU and
                            PLRU for the replacement strategy.
                        </p>
                        <p>
                            As the name implies, LRU (Least Recently Used) will
                            always replace the block that was used least
                            recently. The LRU value in the cache table shows the
                            age of each block. Higher values indicate more
                            recently used blocks.
                        </p>
                        <p>
                            PLRU (Pseudo LRU) is an approximation of LRU which
                            is easier to implement in hardware. It uses a binary
                            tree with the blocks at its leaf nodes. On each
                            non-leaf node is a single bit - a 0 indicates that
                            older blocks are in the upper child tree while a 1
                            indicates that older blocks are in the lower child
                            tree. <br />
                            When replacing a block, PLRU will choose the one
                            which is oldest according to those bits. Then all
                            bits along the path are flipped to mark it as the
                            most recent. <br />
                            When accessing any block that is stored in the
                            cache, PLRU will update all bits along the path to
                            the new block so they correctly identify it as the
                            newest block. <br />
                            Note that when using PLRU, associativity must be a
                            power of 2 since PLRU uses a binary tree in its
                            state.
                        </p>
                        <p>
                            You can also get a visualization of the cache by
                            selecting it in the drop down menu in the control
                            bar. Note that for performance reasons, this option
                            becomes unavailabe if the cache gets too big. Even
                            with the visualization disabled, you should not make
                            the cache too big since the site may become
                            unresponsive.
                        </p>
                        <p>
                            When using a data cache, misaligned access to the
                            memory is not allowed because it would be unclear
                            what exactly should happen in the cache. For
                            example, the following piece of code would not work
                            since the accessed value crosses a word boundary:
                        </p>
                        <pre class="bg-light">lw x1, -5(x0)</pre>
                    </div>
                </div>
            </div>
            <div class="accordion-item">
                <h3
                    class="accordion-header"
                    id="panelsStayOpen-headingThirteen"
                >
                    <button
                        class="accordion-button collapsed"
                        type="button"
                        data-bs-toggle="collapse"
                        data-bs-target="#panelsStayOpen-collapseThirteen"
                        aria-expanded="false"
                        aria-controls="panelsStayOpen-collapseThirteen"
                    >
                        ECALLs
                    </button>
                </h3>
                <div
                    id="panelsStayOpen-collapseThirteen"
                    class="accordion-collapse collapse"
                    aria-labelledby="panelsStayOpen-headingThirteen"
                >
                    <div class="accordion-body">
                        <p>
                            Environment calls (ECALLs) can be used for
                            interacting with the environment - currently, ECALLs
                            can be used for printing to the console or stopping
                            the simulation. Each ECALL has a different code
                            which must be loaded into register <code>a7</code>.
                            Some ECALLs also require an argument which must be
                            loaded into register <code>a0</code>. The supported
                            ECALLs are identical to those of Ripes.
                        </p>

                        <p>
                            Note that our visualization of the pipeline during
                            an ECALL is not fully correct. The pipeline might
                            get flushed unnecessarily and we also dont halt the
                            pipeline until the ECALL has finished - instead, the
                            entire ecall is being executed in a single cycle (in
                            the execute stage).
                        </p>

                        <div class="table-responsive">
                            <table class="table table-bordered table-hover">
                                <thead>
                                    <tr>
                                        <th>a7</th>
                                        <th>a0</th>
                                        <th>Description</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>1</td>
                                        <td>integer to print</td>
                                        <td>
                                            Prints <code>a0</code> as signed
                                            integer.
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>2</td>
                                        <td>float to print</td>
                                        <td>
                                            Prints <code>a0</code> as a floating
                                            point number.
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>4</td>
                                        <td>string to print</td>
                                        <td>
                                            Prints the null terminated string
                                            whose first character is stored at
                                            the address in
                                            <code>a0</code>.
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>10</td>
                                        <td>-</td>
                                        <td>
                                            Stops the simulation with code 0.
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>11</td>
                                        <td>char to print</td>
                                        <td>
                                            Prints <code>a0</code> as ASCII
                                            character
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>34</td>
                                        <td>hex to print</td>
                                        <td>
                                            Prints <code>a0</code> as
                                            hexadecimal nuber
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>35</td>
                                        <td>binary to print</td>
                                        <td>
                                            Prints <code>a0</code> as binary
                                            number.
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>36</td>
                                        <td>integer to print</td>
                                        <td>
                                            Prints <code>a0</code> as unsigned
                                            integer.
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>93</td>
                                        <td>exit code</td>
                                        <td>
                                            Stops the simulation with code in
                                            <code>a0</code>.
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!--my_acc_marker-->
</template>
