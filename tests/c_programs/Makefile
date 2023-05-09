CC = riscv-none-elf-gcc
CFLAGS=-O0 -march=rv32i

all: add.s

%.s: %.c
	$(CC) $(CFLAGS) -S $< -o $@

.PHONY: clean
clean:
	-rm *.s
