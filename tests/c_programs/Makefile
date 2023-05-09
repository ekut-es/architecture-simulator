CC=riscv-none-elf-gcc
OBJDUMP=riscv-none-elf-objdump
CFLAGS=-O0 -march=rv32i -nostdlib

# -Mno-aliases removed pseudo instructions
# -Mnumeric uses x0-x31 registers instead of ABI names
# --no-show-raw-insn does not show hex code for instructions
# --no-addresses does output instruction addresses
OBJDUMP_FLAGS=-d -Mno-aliases -Mnumeric --no-show-raw-insn --no-addresses

SED_FILTER=sed '/^\(<\|\t\)/!d' | sed 's/<\(.*\)>/\1/'

all: add.s fibonacci.s

%.a: %.c
	$(CC) $(CFLAGS) $< -o $@

add.s: add.a
	$(OBJDUMP) $(OBJDUMP_FLAGS) $<  | $(SED_FILTER) > $@

fibonacci.s: fibonacci.a
	$(OBJDUMP) $(OBJDUMP_FLAGS) $< | $(SED_FILTER) > $@

.PHONY: clean
clean:
	-rm *.s
	-rm *.a
