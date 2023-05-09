CC=riscv-none-elf-gcc
OBJDUMP=riscv-none-elf-objdump
CFLAGS=-O0 -march=rv32i

# -Mno-aliases removed pseudo instructions
# -Mnumeric uses x0-x31 registers instead of ABI names
# --no-show-raw-insn does not show hex code for instructions
# --no-addresses does output instruction addresses
OBJDUMP_FLAGS=-d -Mno-aliases -Mnumeric --no-show-raw-insn --no-addresses

all: add.s fibonacci.s

%.a: %.c
	$(CC) $(CFLAGS) $< -o $@

add.s: add.a
	$(OBJDUMP) $(OBJDUMP_FLAGS) --disassemble=main $< >> $@

fibonacci.s: fibonacci.a
	$(OBJDUMP) $(OBJDUMP_FLAGS) --disassemble=main $< >> $@
	$(OBJDUMP) $(OBJDUMP_FLAGS) --disassemble=fibonacci $< >> $@

.PHONY: clean
clean:
	-rm *.s
	-rm *.a
