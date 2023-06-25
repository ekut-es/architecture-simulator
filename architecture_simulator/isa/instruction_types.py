from dataclasses import dataclass

from architecture_simulator.uarch.architectural_state import ArchitecturalState
from typing import Optional
import fixedint


@dataclass
class Instruction:
    mnemonic: str
    # length of the instruction in bytes. Most instructions are 4 bytes long.
    # If this is not the case, this needs to be shadowed (I hope that that works in python, but we'll se that when we get to it).
    length: int = 4

    def __init__(self, **kwargs):
        self.mnemonic = kwargs["mnemonic"]

    def behavior(self, architectural_state: ArchitecturalState):
        pass

    def access_register_file(self, architectural_state: ArchitecturalState):
        pass

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        pass

    def control_unit_signals(self):
        pass

    def get_write_register(self):
        pass

    def memory_access(
        self,
        address: Optional[int],
        write_data: Optional[int],
        architectural_state: ArchitecturalState,
    ):
        pass

    def write_back(
        self,
        write_register: Optional[int],
        write_data: Optional[int],
        architectural_state: ArchitecturalState,
    ):
        pass


class RTypeInstruction(Instruction):
    """Create an R-Type instruction

    Args:
        rd (int): register destination
        rs1 (int): source register 1
        rs2 (int): source register 2
    """

    def __init__(self, rd: int, rs1: int, rs2: int, **args):
        super().__init__(**args)
        self.rs1 = rs1
        self.rs2 = rs2
        self.rd = rd

    def __repr__(self) -> str:
        return f"{self.mnemonic} x{self.rd}, x{self.rs1}, x{self.rs2}"

    def access_register_file(self, architectural_state: ArchitecturalState):
        return (
            self.rs1,
            self.rs2,
            int(architectural_state.register_file.registers[self.rs1]),
            int(architectural_state.register_file.registers[self.rs2]),
            None,
        )

    def control_unit_signals(self):
        from ..uarch.pipeline import ControlUnitSignals

        # jump, alu_op
        return ControlUnitSignals(
            alu_src=False,
            mem_to_reg=False,
            reg_write=True,
            mem_read=False,
            mem_write=False,
            branch=False,
            jump=False,
            alu_op=2,
        )

    def get_write_register(self):
        return self.rd

    def memory_access(
        self,
        address: Optional[int],
        write_data: Optional[int],
        architectural_state: ArchitecturalState,
    ):
        return None

    def write_back(
        self,
        write_register: Optional[int],
        write_data: Optional[int],
        architectural_state: ArchitecturalState,
    ):
        assert write_register is not None
        assert write_data is not None
        architectural_state.register_file.registers[
            write_register
        ] = fixedint.MutableUInt32(write_data)


class CSRTypeInstruction(Instruction):
    """Create a CSR-Type instruction

    Args:
        rd (int): register destination
        csr (int): the control/status register's index
        rs1 (int): source register 1
    """

    def __init__(self, rd: int, csr: int, rs1: int, **args):
        super().__init__(**args)
        self.rd = rd
        self.csr = csr
        self.rs1 = rs1

    def __repr__(self) -> str:
        return f"{self.mnemonic} x{self.rd}, {hex(self.csr)}, x{self.rs1}"


class CSRITypeInstruction(Instruction):
    """Create a CSRI-Type instruction

    Args:
        rd (int): register destination
        csr (int): the control/status register's index
        uimm (int): immediate
    """

    def __init__(self, rd: int, csr: int, uimm: int, **args):
        super().__init__(**args)
        self.rd = rd
        self.csr = csr
        self.uimm = uimm & (2**5) - 1  # [0:5]

    def __repr__(self) -> str:
        return f"{self.mnemonic} x{self.rd}, {hex(self.csr)}, {self.uimm}"


class BTypeInstruction(Instruction):
    def __init__(self, rs1: int, rs2: int, imm: int, **args):
        """Create a B-Type instruction
        Note: These B-Type-Instructions will actually set the pc to 2*imm-4, because the simulator will always add 4 to the pc.

        Args:
            rs1 (int): source register 1
            rs2 (int): source register 2
            imm (int): offset to be added to the pc. Needs to be a 12 bit signed integer. Interpreted as multiple of 2 bytes.
        """
        super().__init__(**args)
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = (imm & 2047) - (imm & 2048)  # 12-bit sext

    def __repr__(self) -> str:
        return f"{self.mnemonic} x{self.rs1}, x{self.rs2}, {self.imm*2}"

    def access_register_file(self, architectural_state: ArchitecturalState):
        return (
            self.rs1,
            self.rs2,
            architectural_state.register_file.registers[self.rs1],
            architectural_state.register_file.registers[self.rs2],
            self.imm,
        )

    def control_unit_signals(self):
        from ..uarch.pipeline import ControlUnitSignals

        return ControlUnitSignals(
            alu_src=False,
            mem_to_reg=None,
            reg_write=False,
            mem_read=False,
            mem_write=False,
            branch=True,
            jump=False,
            alu_op=1,
        )

    def get_write_register(self):
        return None

    # TODO: no longer sub by 4. This no longer happens.


class STypeInstruction(Instruction):
    """Create an S-Type instruction

    Args:
        rs1 (int): source register 1
        rs2 (int): source register 2
        imm (int): offset to be added to the rs1
    """

    def __init__(self, rs1: int, rs2: int, imm: int, **args):
        super().__init__(**args)
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = (imm & 2047) - (imm & 2048)  # 12-bit sext

    def __repr__(self) -> str:
        return f"{self.mnemonic} x{self.rs2}, {self.imm}(x{self.rs1})"

    def access_register_file(self, architectural_state: ArchitecturalState):
        return (
            self.rs1,
            self.rs2,
            architectural_state.register_file.registers[self.rs1],
            architectural_state.register_file.registers[self.rs2],
            self.imm,
        )

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        pass

    def control_unit_signals(self):
        pass

    def get_write_register(self):
        pass

    def memory_access(
        self,
        address: Optional[int],
        write_data: Optional[int],
        architectural_state: ArchitecturalState,
    ):
        pass

    def write_back(
        self,
        write_register: Optional[int],
        write_data: Optional[int],
        architectural_state: ArchitecturalState,
    ):
        pass


class UTypeInstruction(Instruction):
    def __init__(self, rd: int, imm: int, **args):
        super().__init__(**args)
        self.rd = rd
        self.imm = (imm & (2**19) - 1) - (imm & 2**19)  # 20-bit sext

    def __repr__(self) -> str:
        return f"{self.mnemonic} x{self.rd}, {self.imm}"


class JTypeInstruction(Instruction):
    def __init__(self, rd: int, imm: int, **args):
        super().__init__(**args)
        self.rd = rd
        self.imm = (imm & (2**19) - 1) - (imm & 2**19)  # 20-bit sext

    def __repr__(self) -> str:
        return f"{self.mnemonic} x{self.rd}, {self.imm*2}"


class fence(Instruction):
    def __init__(self, **args):
        super().__init__(**args)

    # TODO: Change me, if Fence gets implemented
    # def __repr__(self) -> str:
    #    return f"{self.mnemonic}"


class ITypeInstruction(Instruction):
    def __init__(self, rd: int, rs1: int, imm: int, **args):
        """Create a I-Type instruction

        Args:
            imm (int): offset to be further progressed by the instruction
            rs1 (int): source register 1
            rd (int): destination register
        """
        super().__init__(**args)
        self.rs1 = rs1
        self.rd = rd
        self.imm = (imm & (2**11) - 1) - (imm & 2**11)  # 12-bit sext

    def __repr__(self) -> str:
        from architecture_simulator.isa.rv32i_instructions import (
            LB,
            LH,
            LW,
            LBU,
            LHU,
            ECALL,
            EBREAK,
        )

        memory_instructions = (LB, LH, LW, LBU, LHU)
        e_instructions = (ECALL, EBREAK)
        if isinstance(self, memory_instructions):
            return f"{self.mnemonic} x{self.rd}, {self.imm}(x{self.rs1})"
        elif isinstance(self, e_instructions):
            return f"{self.mnemonic}"
        else:
            return f"{self.mnemonic} x{self.rd}, x{self.rs1}, {self.imm}"


class ShiftITypeInstruction(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int, **args):
        """Create an I-Type instruction that requires shamt

        Args:
            imm (int): shift amount
            rs1 (int): source register 1
            rd (int): destination register
        """
        super().__init__(rd, rs1, imm, **args)
        self.imm = imm & (2**5) - 1  # [0:5]

    def __repr__(self) -> str:
        return f"{self.mnemonic} x{self.rd}, x{self.rs1}, {self.imm}"


class EmptyInstruction(Instruction):
    def __init__(self, **kwargs):
        super().__init__(mnemonic="Empty")

    def access_register_file(self, architectural_state: ArchitecturalState):
        return (None, None, None, None, None)

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        return (None, None)

    def control_unit_signals(self):
        from ..uarch.pipeline import ControlUnitSignals

        return ControlUnitSignals()

    def get_write_register(self):
        return None

    def memory_access(
        self,
        address: Optional[int],
        write_data: Optional[int],
        architectural_state: ArchitecturalState,
    ):
        return None

    def write_back(
        self,
        write_register: Optional[int],
        write_data: Optional[int],
        architectural_state: ArchitecturalState,
    ):
        pass
