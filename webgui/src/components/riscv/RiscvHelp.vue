<!-- The riscv help page content. -->
<script setup>
import riscv_instructions from "@/data/riscv_instructions.json";
import RiscvHelpTable from "./RiscvHelpTable.vue";
</script>
<template>
    <div class="container-fluid">
        <h1>RISC-V</h1>
        <h2 id="instructions">Instructions</h2>
        <p>
            This simulator supports a subset of the RISC-V32 ISA. The supported
            instructions are listed below.
        </p>
        <div class="accordion" id="accordionPanelsStayOpenInstructions">
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
                        Computational
                    </button>
                </h3>
                <div
                    id="panelsStayOpen-collapseOne"
                    class="accordion-collapse collapse"
                    aria-labelledby="panelsStayOpen-headingOne"
                >
                    <div class="accordion-body">
                        <RiscvHelpTable
                            :instructions="riscv_instructions['computational']"
                        />
                        <p>
                            Notes: <br />
                            - Instructions marked with (M) are part of the "M”
                            Standard Extension for Integer Multiplication and
                            Division.
                            <br />
                            - Unless otherwise specified, the immediate
                            (<code>imm</code>) of I-type instructions has a
                            length of 12 bits and is sign extended to 32 bits.
                            <br />
                            - The immediate (<code>imm</code>) of U-Type
                            instructions has a length of 20 bits and is sign
                            extended to 32 bits.
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
                        Memory-Accesses
                    </button>
                </h3>
                <div
                    id="panelsStayOpen-collapseTwo"
                    class="accordion-collapse collapse"
                    aria-labelledby="panelsStayOpen-headingTwo"
                >
                    <div class="accordion-body">
                        <RiscvHelpTable
                            :instructions="
                                riscv_instructions['memory-accesses']
                            "
                        />
                        <p>
                            Notes: <br />
                            - The immediate (imm) of the instructions in this
                            paragraph has a length of 12 bits and is sign
                            extended to 32 bits.
                            <br />
                            - <code>var</code> is a variable name,
                            <code>index</code> is an optional array index.
                        </p>
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
                        Jumps and Branches
                    </button>
                </h3>
                <div
                    id="panelsStayOpen-collapseThree"
                    class="accordion-collapse collapse"
                    aria-labelledby="panelsStayOpen-headingThree"
                >
                    <div class="accordion-body">
                        <RiscvHelpTable
                            :instructions="
                                riscv_instructions['jumps and branches']
                            "
                        />
                        <p>
                            Notes: <br />
                            - JAL instructions encode the address to jump to
                            (<code>addr</code>), relative to the current pc in a
                            21 bit immediate that is sign extended to 32 bits
                            and added to the current pc.<br />
                            - The JALR immediate (<code>imm</code>) has a length
                            of 12 bits and is sign extended to 32 bits.<br />
                            - The immediate (<code>imm</code> ) of B-type
                            instructions has a length of 13 bits and is sign
                            extended to 32 bits.<br />
                            - <code>offset</code> is optional, and in
                            hexadecimal format.
                        </p>
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
                        System Instructions
                    </button>
                </h3>
                <div
                    id="panelsStayOpen-collapseFour"
                    class="accordion-collapse collapse"
                    aria-labelledby="panelsStayOpen-headingFour"
                >
                    <div class="accordion-body">
                        <RiscvHelpTable
                            :instructions="
                                riscv_instructions['system instructions']
                            "
                        />
                        <p>
                            Notes: <br />
                            -
                            <i
                                >CSR Currently not implemented in 5-stage
                                pipeline mode.</i
                            ><br />
                            - The unsigned immediate (<code>uimm</code>) has a
                            length of 5 bits.
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <h2 id="other">Other</h2>

        <div class="accordion" id="accordionPanelsStayOpenOther">
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
                        id="riscv-help-ecalls"
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
</template>
