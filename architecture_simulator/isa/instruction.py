# @dataclass
class Instruction:
    # length refers to how many addresses the instruction takes up in the instruction memory it is designed to be stored in.
    # So if an instruction takes up 4 bytes, length should be 4 if the memory is byte addressed but 1 if the memory is word addressed.
    length: int
