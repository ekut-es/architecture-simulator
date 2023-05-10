CC=riscv-none-elf-gcc
OBJDUMP=riscv-none-elf-objdump
CFLAGS=-O0 -march=rv32i -nostdlib --entry main

# -Mno-aliases removed pseudo instructions
# -Mnumeric uses x0-x31 registers instead of ABI names
# --no-show-raw-insn does not show hex code for instructions
# --no-addresses does output instruction addresses
OBJDUMP_FLAGS=-d -Mno-aliases -Mnumeric --no-show-raw-insn --no-addresses

SED_FILTER=sed '/^\(<\|\t\)/!d' | sed 's/<\(.*\)>/\1/'

all: add.s fibonacci.s

%.elf: %.c
	$(CC) $(CFLAGS) $< -o $@

%.s: %.elf
	$(OBJDUMP) $(OBJDUMP_FLAGS) $<  | $(SED_FILTER) > $@

.PHONY: clean
clean:
	-rm *.s
	-rm *.elf
