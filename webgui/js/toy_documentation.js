const toyDocumentation = /*html*/ `<div class="container-fluid">
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
        <code>addr</code> of an instruction is a 12 bit value that can either be
        given as decimal or hexadecimal number, or it can be the name of a label
        or a variable. Hexadecimal numbers have to be prepended by a dollar sign
        like this: <code>$400</code>.
    </p>

    <h2>Comments</h2>
    <p>Comments start with a <code>#</code>.</p>
    <pre class="bg-light"># This is a comment</pre>

    <h2>Labels and variables</h2>
    <p>
        Labels and variables are both names that can be used instead of
        addresses.<br />
        Labels reference a position in the program and are used as destination
        address for branch instructions. They are declared by typing the name of
        the label, followed by a colon.<br />
        Variables can be manually set to reference an arbitrary address and they
        are used to point to some location in memory. They are declared by
        typing the name of the variable, followed by an equals sign and the
        desired address. Note that variables will be processed once before the
        execution of the program. They can be referenced everywhere in the
        program and you cannot reassign a variable name.
    </p>
    <pre class="bg-light">
loop:
LDA counter
DEC
STO counter
BRZ end
ZRO
BRZ loop
end:

counter=$400</pre
    >

    <h2>Data write directives</h2>
    <p>
        It is possible to write data to the data memory before the execution of
        the program with data write directives. To create such a directive, type
        a colon, followed by an address, then another colon and the desired
        value. Note that data write directives are also processed exactly once
        before the execution of the program, just like variables. The data will
        not be written to the memory every time the program "steps over a line"
        containing a data write directive.
    </p>
    <pre class="bg-light">
:$400:25
:1025:$FF
LDA $400
...</pre
    >

    <h2>Instruction and data memory</h2>
    <p>
        This simulator uses separate data and instruction memories. By default,
        the instruction memory uses addresses from 0 to 1023, while the data
        memory uses addresses from 1024 to 4095. That means you can only use up
        to 1024 instructions and load and store instructions can only use
        addresses that lie within the data memory. That also means that it is
        not possible to alter the instruction memory "at runtime".
    </p>

    <h2>Examples</h2>
    <pre class="bg-light">
# computes the sum of the numbers from 1 to n
# result gets saved in MEM[1025]
Loopcount = $400
Result = $401
:$400:20 # enter n here

LDA Loopcount # skip to the end if n=0
BRZ end
loop:
LDA Result
ADD Loopcount
STO Result
LDA Loopcount
DEC
STO Loopcount
BRZ end
ZRO
BRZ loop
end:
</pre
    >
</div>`;
