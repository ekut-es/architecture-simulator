"""type stubs for js functions"""

def update_register_table(reg: int, representations: tuple, abi_name: str) -> None: ...
def update_single_register(reg: int, val: int) -> None: ...
def update_memory_table(address: str, val: str) -> None: ...
def update_single_memory_address(address: str, val: str) -> None: ...
def update_instruction_table(address, val, stage) -> None: ...
def clear_memory_table() -> None: ...
def highlight(position: int, str: str) -> None: ...
def remove_all_highlights() -> None: ...
def update_IF_Stage(instruction, address_of_instruction) -> None: ...
def update_ID_Stage(
    register_read_addr_1,
    register_read_addr_2,
    register_read_data_1,
    register_read_data_2,
    imm,
    control_unit_signals,
) -> None: ...
def update_EX_Stage(
    alu_in_1,
    alu_in_2,
    register_read_data_2,
    imm,
    result,
    comparison,
    pc_plus_imm,
    control_unit_signals,
) -> None: ...
def update_MA_Stage(
    memory_address,
    result,
    memory_write_data,
    memory_read_data,
    comparison,
    comparison_or_jump,
    pc_plus_imm,
    control_unit_signals,
) -> None: ...
def update_WB_Stage(
    register_write_data,
    write_register,
    memory_read_data,
    alu_result,
    control_unit_signals,
) -> None: ...

# def update_output(output_string: str) -> None: ...
def clear_register_table() -> None: ...
def clear_instruction_table() -> None: ...
def set_output(str: str) -> None: ...

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
from architecture_simulator.uarch.architectural_state import RegisterFile, Memory
from architecture_simulator.isa.instruction_types import Instruction
from architecture_simulator.isa.rv32i_instructions import ADD
from architecture_simulator.uarch.architectural_state import ArchitecturalState
from architecture_simulator.simulation.simulation import Simulation
import fixedint
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
#print(json.dumps({"cmd_list": json_array}))
simulation = Simulation(state=ArchitecturalState(register_file=RegisterFile()), instructions={})
#print(simulation)
state = ArchitecturalState(register_file=RegisterFile(registers=[]))
state.register_file.registers[1] = fixedint.MutableUInt32(0x_80_00_00_00)
#print(len(state.register_file.registers))
#print([fixedint.MutableUInt32(0) for i in range(32)])
for reg_i in range(len(simulation.state.register_file.registers)):
    print(reg_i,int(simulation.state.register_file.registers[reg_i]))"""

"""d = {1: "a", 2: "b", 4: "c", 3: "d"}
print(sorted(d.items(), key=lambda item: item[0]))"""
