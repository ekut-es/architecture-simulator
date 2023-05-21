"""type stubs for js functions"""

def append_register(reg: int, val: int) -> None: ...
def append_registers(reg_json_str: str) -> None: ...
def update_register(reg: int, val: int) -> None: ...
def append_memory(address: str, val: str) -> None: ...
def append_memories(reg_json_str: str) -> None: ...
def update_memory(address: str, val: str) -> None: ...
def append_instructions(cmd_json_str: str) -> None: ...

"""import json
from architecture_simulator.isa.rv32i_instructions import (
    ADD,
    ADDI,
    AND,
    BEQ,
    BGE,
    JAL,
    JALR,
    LUI,
    LW,
    SW,
)
from architecture_simulator.isa.instruction_types import RTypeInstruction, CSRTypeInstruction, CSRITypeInstruction
str = '{"cmd_list":[{"add":"0x0000", "cmd":"SUB A0, T0, T2"}, {"add":"0x0004", "cmd":"ADD A0, T0, T2"}]}'
str_parsed = json.loads(str)
print(str_parsed["cmd_list"])
for cmd in str_parsed["cmd_list"]:
    print(cmd["cmd"])

instructions={0: ADD(rd=1, rs1=2, rs2=3)}
json_array = []
for address, cmd in instructions.items():
    json_array.append({hex(address): cmd})
print(instructions[0].rd)
#print(json.dumps({"cmd_list": json_array}))"""
