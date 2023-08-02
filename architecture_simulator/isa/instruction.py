# @dataclass
class Instruction:
    """Base class for instructions of all ISAs."""

    # length refers to how many addresses the instruction takes up in the instruction memory it is designed to be stored in.
    # So if an instruction takes up 4 bytes, length should be 4 if the memory is byte addressed but 1 if the memory is word addressed.
    # This might seem weird but it ensures that you can use the InstructionMemory class.
    length: int
