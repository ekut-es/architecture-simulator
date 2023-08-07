# Toy ISA documentation
The architecture simulator supports the Toy ISA. Here is a documentation on which features are currently supported. Since the official documentation is rather sparse, we resolved some things on our own, so things might be different from what you expected.

- Addresses can be entered as decimal numbers (e.g.: `ADD 1030`) or hexadecimal numbers, prepended by a dollar sign (`$`) (e.g.: `ADD $406`).
- There is no size limitation on addresses. If an address is larger than e.g. 4095, it will simply overflow.
- Right now, data and instructions are stored separately. By default, the instruction memory uses addresses from 0 to 1023 and data memory uses addresses from 1024 to 4095. It is not possible to make an instruction read or write to the instruction memory, nor is it possible to read an instruction from the data memory. This might change later so that instructions and data are truly stored in the same memory.
- Comments are started with a hash sign (`#`). The rest of the line will be ignored by the parser.
- Labels are supported: Labels are declared by writing the label name followed by a colon (`:`) (e.g.: `my_Label:`). Note that labels can be used for any instructions that take addresses, not just for `BRZ`.
- Variables are supported: To declare a variable, write the name of the variable, followed by an equals sign (`=`) and the value of the variable (e.g.: `myVar = 240`). The value can again be given as decimal or hexadecimal value. Variables are simply names for addresses, much like labels, except you can manually set a fixed address.
- Variable names and label names are case sensitive. They may consist of letters, numbers and underscores, although they may not start with a number. Also note that you cannot use the same name for a label and a variable, since they will both simply create names that you can use instead of addresses.
- It is also possible to put commands in the assembly code to directly store values in memory. To do so, enter a colon (`:`) and an address, followed by another colon and the desired value. Addresses and values can again be given as decimal or hexadecimal values.
- Note that labels, variables and data write commands will be processed exactly once, before the program execution starts. They will not be executed every time the program reaches that line.
