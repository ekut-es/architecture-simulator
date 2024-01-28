<!-- The TOY help page -->
<template>
    <div class="container-fluid">
        <h2>Instructions</h2>
        <div class="table-responsive">
            <table class="table table-bordered table-hover">
                <thead>
                    <tr>
                        <th>Instruction</th>
                        <th>Operation</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>
                            <code>STO addr</code>
                        </td>
                        <td>
                            <code>MEM[addr] = ACCU</code>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <code>LDA addr</code>
                        </td>
                        <td>
                            <code>ACCU = MEM[addr]</code>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <code>BRZ addr</code>
                        </td>
                        <td>
                            <code>PC = addr if (ACCU == 0)</code>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <code>ADD addr</code>
                        </td>
                        <td>
                            <code>ACCU += MEM[addr]</code>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <code>SUB addr</code>
                        </td>
                        <td>
                            <code>ACCU -= MEM[addr]</code>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <code>OR addr</code>
                        </td>
                        <td>
                            <code>ACCU |= MEM[addr]</code>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <code>AND addr</code>
                        </td>
                        <td>
                            <code>ACCU &= MEM[addr]</code>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <code>XOR addr</code>
                        </td>
                        <td>
                            <code>ACCU ^= MEM[address]</code>
                        </td>
                    </tr>
                    <tr>
                        <td><code>NOT</code></td>
                        <td>
                            <code>ACCU = ~ACCU</code>
                        </td>
                    </tr>
                    <tr>
                        <td><code>INC</code></td>
                        <td>
                            <code>ACCU += 1</code>
                        </td>
                    </tr>
                    <tr>
                        <td><code>DEC</code></td>
                        <td>
                            <code>ACCU -= 1</code>
                        </td>
                    </tr>
                    <tr>
                        <td><code>ZRO</code></td>
                        <td>
                            <code>ACCU = 0</code>
                        </td>
                    </tr>
                    <tr>
                        <td><code>NOP</code></td>
                        <td>
                            <code>no operation</code>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        <p>
            Note that the address
            <code>addr</code> of an instruction is a 12 bit value that can
            either be given as decimal or hexadecimal number, or it can be the
            name of a label or a variable. Hexadecimal numbers have to be
            prepended by '0x' like this: <code>0x400</code>.
        </p>

        <h2>Comments</h2>
        <p>Comments start with a <code>#</code>.</p>
        <pre class="bg-light"># This is a comment</pre>

        <h2>Labels</h2>
        <p>
            Labels are names that can be used instead of addresses.<br />
            Labels reference a position in the program and are used as
            destination addresses for branch instructions or to reference an
            instruction. They are declared by typing the name of the label,
            followed by a colon. Note that indenting the following code section
            is optional.<br />
        </p>
        <pre class="bg-light">
loop:
    LDA 0x400
    DEC
    STO 0x400
    BRZ end
    ZRO
    BRZ loop
end:
</pre
        >

        <h2>Segments and variables</h2>
        In addition to the program code, the simulator supports a data segment.
        It can be used to store variables and arrays in the processor's
        memory.<br />

        In order to define a data segment, the
        <code>.data</code> directive is used, while the
        <code>.text</code> directive designates the code segment. <br />
        The following example demonstrates how to declare and use variables and
        arrays: <br />
        <br />
        <pre class="bg-light">
.data
    my_array: .word 7, 0x00F, 3 # my_array points to the address of the first element of the array
    my_var: .word 7
    my_result: .word 0
.text
    # check if the first element of my_array is equal to my_var and store result in my_result
    LDA my_array
    SUB my_var
    BRZ true
    ZRO
    BRZ end
    true:
        INC
        STO my_result
    end:</pre
        >
        <p>
            Note that similarly to labels, indentation is optional. <br />
            If no directives are given, the entire input is interpreted as
            code.<br />
            Similarly, if a <code>.data</code> but no
            <code>.text</code> directive is given, every line before the data
            segment is interpreted as code.
            <br />
            There is no fixed segmentation order. However, declaring multiple
            segments of the same type will throw an error.
        </p>
        <h2>Memory</h2>
        <p>
            The simulator uses one memory of 4096 16 bit words for instructions
            and data.<br />
            Instructions get written to the beginning of the memory space. They
            can be modified "at runtime" (see Examples).<br />
            Any value in the memory can be interpreted as an instruction. To
            still know when to stop, we use the last instruction written in the
            code editor. If the program counter gets higher, the simulation will
            stop.<br />
            Variables and arrays get written to the end of the memory (the first
            variable declared will have the highest memory address). Note that
            the elements of an array still get written in ascending order.
        </p>

        <h2>Examples</h2>

        <h4>Example 1:</h4>
        <pre class="bg-light">
# computes the sum of the numbers from 1 to n

.data
    n: .word 10 # enter n here
    result: .word 0

.text
    LDA n # skip to the end if n=0
    BRZ end
    loop:
        LDA result
        ADD n
        STO result
        LDA n
        DEC
        STO n
        BRZ end
        ZRO
        BRZ loop
    end:
</pre
        >
        <h4>Example 2:</h4>
        <pre class="bg-light">
# store second value of my_tuple in my_value

.data
    my_tuple: .word 3, 4
    my_value: .word 0

.text
    LDA my_load_instruction     # load 'LDA my_tuple' (LDA 0xFFE) into accu
    INC                         # increment address in LDA instruction
    STO my_load_instruction     # store 'LDA 0xFFF' at my_load_instruction
    my_load_instruction:        # this label points to the memory location of LDA instruction
    LDA my_tuple                # actually load data at my_tuple + 1 (=0xFFF)
    STO my_value                # store value of second tuple entry at my_value (0xFFD)
</pre
        >
    </div>
</template>
