from architecture_simulator.simulation.riscv_simulation import RiscvSimulation
from architecture_simulator.simulation.toy_simulation import ToySimulation
from typing import Optional, Union
from architecture_simulator.uarch.memory import Memory
from architecture_simulator.uarch.toy.toy_memory import ToyMemory
from architecture_simulator.uarch.riscv.register_file import RegisterFile

from architecture_simulator.uarch.riscv.pipeline import (
    PipelineRegister,
    InstructionExecutionException,
)
from architecture_simulator.isa.riscv.instruction_types import EmptyInstruction
from architecture_simulator.isa.parser_exceptions import ParserException
from abc import ABC, abstractmethod
import os.path
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit import PromptSession

logo = """==========================================================================================
  _____  _____  _____  _____   __      __   _____ _                 _       _
 |  __ \|_   _|/ ____|/ ____|  \ \    / /  / ____(_)               | |     | |
 | |__) | | | | (___ | |   _____\ \  / /  | (___  _ _ __ ___  _   _| | __ _| |_ ___  _ __
 |  _  /  | |  \___ \| |  |______\ \/ /    \___ \| | '_ ` _ \| | | | |/ _` | __/ _ \| '__|
 | | \ \ _| |_ ____) | |____      \  /     ____) | | | | | | | |_| | | (_| | || (_) | |
 |_|  \_\_____|_____/ \_____|      \/     |_____/|_|_| |_| |_|\__,_|_|\__,_|\__\___/|_|

=========================================================================================="""

greetings = """Hello user! For information on available commands type \'help\'."""

help_information = """
==========================================================================
List of available commands:

'load <file>' will create a new simulation using the instructions and
              data section provided in the file with optional arguments.
    Select the mode of simulation (default is singleStage):
    '-singleStage'
    or
    '-toyProcessor'
    or
    '-fiveStage'
    Turn off data hazard detection in five-stage mode:
    '-noDataHazardDetection'
    Conduct some number of execution cycles or run until done:
    '-step=<number of steps>'
    or
    '-run'
    Change the display format (default is sdec):
    '-sdec'
    or
    '-udec'
    or
    '-hex'
    or
    '-bin'

'step <number>' will execute <number> execution cycles or fewer,
                if done earlier.

'run' will conduct execution cycles until done
      or the program is manually aborted by the user.

'show <format>' will change the display format and display the
                  state in that format.
    <format> = 'sdec' or 'udec' or 'hex' or 'bin'.

'help' will bring up this help page.

'exit' will close the program.
=========================================================================="""

# Args of load command
mode_args = ["-singlestage", "-toyprocessor", "-fivestage"]
execution_args = ["-run"]  # step=<int>

# Modes for displaying register and memory values
display_modes = ["sdec", "udec", "hex", "bin"]
display_args = [("-" + el) for el in display_modes]


def main():
    print(logo)
    print(greetings)

    sim: Optional[Union[ToySimulation, RiscvSimulation]] = None
    display_mode = "sdec"
    list_of_commands: list[Command] = [
        HelpCommand(),
        LoadCommand(),
        RunCommand(),
        StepCommand(),
        ShowCommand(),
        ExitCommand(),
    ]
    list_of_command_names = [cmd.get_name() for cmd in list_of_commands]
    stop_flag = False

    history = (
        InMemoryHistory()
    )  # enables use of arrow keys, to see previously entered commands
    session = PromptSession(
        history=history, completer=LoadCommandCompleter()
    )  # LoadCommandCompleter provides auto completion for the file path in the load command

    while True:
        read_command = []
        try:
            read_command = session.prompt(">>>").strip().lower().split()
        except KeyboardInterrupt:
            break
        if len(read_command) == 0:
            continue
        if read_command[0] not in list_of_command_names:
            print(
                f"{read_command[0]} is no available command. Type 'help' to get a list of available commands."
            )
            continue
        for cmd in list_of_commands:
            if cmd.get_name() == read_command[0]:
                cmd_output = cmd(sim, read_command, display_mode)
                if cmd_output.stop:
                    stop_flag = True
                    break
                sim = cmd_output.sim
                if not cmd_output.change_display_mode_to == "":
                    display_mode = cmd_output.change_display_mode_to
                print(cmd_output.output)

        if stop_flag:
            break


def resolve_file_path(file_path):
    """
    Resolves absolute, relative filepaths and filepaths including ~.

    Parameters:
    file_path :str

    Returns:
    str
    """
    expanded = os.path.expanduser(file_path)
    if os.path.isabs(expanded):
        return expanded
    else:
        cwd = os.getcwd()
        return os.path.join(cwd, expanded)


def display(sim: Union[ToySimulation, RiscvSimulation], display_mode: str) -> str:
    """
    Produces a representation of the architectural state of a toy or risv Simulation.

    Parameters:
    sim : Union[ToySimulation, RiscvSimulation]
    display_mode: str

    Returns:
    str
    """
    if isinstance(sim, RiscvSimulation):
        hline = "=" * 53 + "\n"
        res = "Architectural sate:\n"
        res += hline
        res += reg_file_repr(sim.state.register_file, display_mode)
        res += hline
        res += memory_repr(sim.state.memory, display_mode)
        res += hline
        if sim.mode == "five_stage_pipeline":
            res += five_stage_pipeline_repr(sim.state.pipeline.pipeline_registers)
            res += hline
        res += f"PC: {sim.state.program_counter} | Instruction at PC: {'#####' if not sim.state.instruction_at_pc() else str(sim.state.instruction_memory.read_instruction(sim.state.program_counter))}\n"
        res += hline
        res += "Performance Metrics:\n"
        res += sim.state.performance_metrics.__repr__()
        res += hline
        return res
    else:
        hline = "=" * 35 + "\n"
        res = "Architectural state:\n"
        res += hline
        res += toy_memory_repr(sim.state.data_memory, display_mode)
        res += hline
        res += f"PC: {sim.state.program_counter} | Instruction at PC: {'#####' if not sim.state.instruction_at_pc() else str(sim.state.instruction_memory.read_instruction(int(sim.state.program_counter)))}\n"
        res += hline
        res += f"Accu: {sim.state.accu}\n"
        res += hline
        res += "Performance Metrics:\n"
        res += sim.state.performance_metrics.__repr__()
        res += hline
        return res


def reg_file_repr(register_file: RegisterFile, display_mode: str) -> str:
    """
    Produces a representation of a RegisterFile.

    Parameters:
    register_file : RegisterFile
    display_mode: str

    Returns:
    str
    """
    if display_mode == "sdec":
        return dec_reg_file_repr(register_file, signed=True)
    elif display_mode == "udec":
        return dec_reg_file_repr(register_file, signed=False)
    elif display_mode == "hex":
        return hex_reg_file_repr(register_file)
    elif display_mode == "bin":
        return bin_reg_file_repr(register_file)
    else:
        return "Error!"


def bin_reg_file_repr(register_file: RegisterFile) -> str:
    """
    Produces a binary representation of a RegisterFile.

    Parameters:
    register_file : RegisterFile

    Returns:
    str
    """
    res = ""
    repr_dict = register_file.reg_repr()
    for i in range(len(register_file.registers)):
        res += f"Register {pad_num(i, 2)}: {repr_dict[i][0]}\n"
    return res


def hex_reg_file_repr(register_file: RegisterFile) -> str:
    """
    Produces a hex representation of a RegisterFile.

    Parameters:
    register_file : RegisterFile

    Returns:
    str
    """
    height = len(register_file.registers) // 2
    repr_dict = register_file.reg_repr()
    res = ""
    for i in range(height):
        res += f"Register {pad_num(i, 2)}: {repr_dict[i][2]} |Register {pad_num(i + height, 2)}: {repr_dict[i+ height][2]}\n"
    return res


def dec_reg_file_repr(register_file: RegisterFile, signed: bool) -> str:
    """
    Produces a decimal representation of a RegisterFile.

    Parameters:
    register_file : RegisterFile+
    signed: bool

    Returns:
    str
    """
    height = len(register_file.registers) // 2
    repr_dict = register_file.reg_repr()
    res = ""
    for i in range(height):
        if signed:
            num_left = repr_dict[i][3]
            num_right = repr_dict[i + height][3]
        else:
            num_left = repr_dict[i][1]
            num_right = repr_dict[i + height][1]
        res += f"Register {pad_num(i, 2)}: {pad_num(num_left, 12)} | Register {pad_num(i + height,2)}: {pad_num(num_right, 12)}\n"
    return res


def pad_num(num: Union[int, str], length: int) -> str:
    """Converts num to a string if it is not already a string and pads it to have a given length.

    Args:
        num (Union[int, str]): the number or string to be padded.
        length (int): the desired length of the padded string.

    Returns:
        str: a padded string.
    """
    return " " * (length - len(str(num))) + str(num)


def memory_repr(mem: Memory, display_mode: str) -> str:
    """
    Produces a representation of a Memory.

    Parameters:
    mem : Memory
    display_mode: str

    Returns:
    str
    """
    repr_dict = mem.memory_wordwise_repr()

    if not bool(repr_dict):
        return "Memory: empty\n"
    if display_mode not in display_modes:
        return ""
    if display_mode == "sdec" or display_mode == "udec":
        res = "Memory:\nAddress          Word\n" + "=" * 21 + "\n"
    elif display_mode == "hex":
        res = "Memory:\nAddress           Word\n" + "=" * 22 + "\n"
    else:
        res = (
            "Memory:\nAddress                                   Word\n"
            + "=" * 46
            + "\n"
        )

    for key in sorted(repr_dict.keys()):
        key_hex = (str(hex(key))[2:]).upper()
        key_repr = "0" * (8 - len(key_hex)) + key_hex
        if display_mode == "sdec":
            res += f"{key_repr} {pad_num(repr_dict[key][3], 12)}\n"
        elif display_mode == "udec":
            res += f"{key_repr} {pad_num(repr_dict[key][1], 12)}\n"
        elif display_mode == "hex":
            res += f"{key_repr} | {repr_dict[key][2]}\n"
        else:  # 'bin' case
            res += f"{key_repr} | {repr_dict[key][0]}\n"

    return res


def five_stage_pipeline_repr(registers: list[PipelineRegister]) -> str:
    """
    Produces a representation of the stages the five stage pipeline.

    Parameters:
    registers: list[PipelineRegister]

    Returns:
    str
    """
    res = "Pipeline Stages:\n"
    names = ["IF: ", "ID: ", "EX: ", "MEM:", "WB: "]
    for name, reg in zip(names, registers):
        if isinstance(reg.instruction, EmptyInstruction):
            res += f"{name} ########\n"
        else:
            res += f"{name} {str(reg.instruction)}\n"
    return res


def toy_memory_repr(mem: ToyMemory, display_mode: str) -> str:
    """
    Produces a representation of the toy processor memory

        Parameters:
        mem: ToyMemory
        display_mode: str

        Returns:
        str
    """
    repr_dict = mem.memory_repr()
    if not bool(repr_dict):
        return "Memory: empty\n"
    if display_mode not in display_modes:
        return ""
    if display_mode == "sdec" or display_mode == "udec":
        res = "Memory:\nAddress   HalfWord\n" + "=" * 18 + "\n"
    elif display_mode == "hex":
        res = "Memory:\nAddress HalfWord\n" + "=" * 16 + "\n"
    else:
        res = "Memory:\nAddress             HalfWord\n" + "=" * 28 + "\n"

    for key in sorted(repr_dict.keys()):
        key_hex = (str(hex(key))[2:]).upper()
        key_repr = "0" * (8 - len(key_hex)) + key_hex
        if display_mode == "sdec":
            res += f"{key_repr}    {pad_num(repr_dict[key][3], 6)}\n"
        elif display_mode == "udec":
            res += f"{key_repr}    {pad_num(repr_dict[key][1], 6)}\n"
        elif display_mode == "hex":
            res += f"{key_repr} | {repr_dict[key][2]}\n"
        else:  # "bin" case
            res += f"{key_repr} | {repr_dict[key][0]}\n"

    return res


def step(
    sim: Union[ToySimulation, RiscvSimulation], num_str: str, display_mode: str
) -> str:
    """
    Implements the functionality of the step command.
    num_str steps will be executed on the sim and a output string will be generated.
    This function does all error handling and will stop, if the simulation is done early.

        Parameters:
        sim: Union[ToySimulation, RiscvSimulation]
        num_str: str
        display_mode: str

        Returns:
        str
    """
    num_int = 0
    res = ""
    try:
        num_int = int(num_str)
    except ValueError:
        return f"{num_str} could not be cast to an int."
    for i in range(1, num_int + 1):
        try:
            if not sim.step():
                res += f"Simulation done after {i} steps.\n"
                break
        except InstructionExecutionException as e:
            res = (
                f"After {i-1} successful steps this exception occured:\n"
                + e.__repr__()
                + "\n"
            )
            break
    return res + display(sim, display_mode)


class CommandResult:
    """
    This class is the return value of the __call__ method of the Command class.\n
    It returns all changes a wants to make to the state of the cli.
    """

    def __init__(
        self,
        output: str,
        sim: Optional[Union[ToySimulation, RiscvSimulation]],
        stop: bool = False,
        change_display_mode_to: str = "",  # "" signals no change is supposed to be made
    ) -> None:
        self.output = output
        self.sim = sim
        self.stop = stop
        self.change_display_mode_to = change_display_mode_to


class Command(ABC):
    """
    Abstract Command class, that all cli command need to implement.
    """

    _name: str = ""

    @abstractmethod
    def __call__(
        self,
        sim: Optional[Union[ToySimulation, RiscvSimulation]],
        command: list[str],
        display_mode: str,
    ) -> CommandResult:
        pass

    def get_name(self):
        return self._name


class LoadCommand(Command):
    """
    LoadCommand implements Command.
    """

    _name = "load"

    def __call__(
        self,
        sim: Optional[Union[ToySimulation, RiscvSimulation]],
        command: list[str],
        display_mode: str,
    ) -> CommandResult:
        """
        Implements the 'load' command, that will load a new simulation.\n
        It may also: step or run it, change the display mode.

        Parameters:
        sim : Optional[Union[ToySimulation, RiscvSimulation]]
        command : list[str]
        display_mode: str

        Returns:
        CommandResult.
        """
        file_path = ""
        file_content = ""
        mode = ""
        data_hazard_detection = True
        dp_mode = display_mode
        new_sim: Union[ToySimulation, RiscvSimulation]
        # Try to load the file
        try:
            file_path = command[1]
        except IndexError:
            return CommandResult("'load' needs a filepath or filename.", sim)
        try:
            with open(resolve_file_path(file_path), "r") as file:
                file_content = file.read()
        except FileNotFoundError:
            return CommandResult(f"File not found at: {file_path}", sim)
        except Exception:
            return CommandResult(
                f"Exception occurred while trying reading the file at : {file_path}",
                sim,
            )

        # check for illegal argument combinations
        if len([el for el in command if el in mode_args]) > 1:
            return CommandResult(
                "You may only provide one argument specifying the simulation mode.", sim
            )
        if len([el for el in command if el == "-run" or el.startswith("-step=")]) > 1:
            return CommandResult(
                "You may only provide one argument specifying execution.", sim
            )
        if len([el for el in command if el in display_args]) > 1:
            return CommandResult(
                "You may only provide one argument specifiying display mode.", sim
            )

        # check for unkown arguments
        unknown_arg = ""
        for el in command[2:]:
            if not (
                el in mode_args + display_args + execution_args
                or el.startswith("-step=")
                or el == "-nodatahazarddetection"
            ):
                unknown_arg = el
        if not unknown_arg == "":
            return CommandResult(
                f"Exception: {unknown_arg} is not a known argument", sim
            )

        # check for execution mode
        if "-toyprocessor" in command:
            mode = "toy_simulation"
        elif "-fivestage" in command:
            mode = "five_stage_pipeline"
        else:
            mode = "single_stage_pipeline"

        # check for no data hazard detection
        if not mode == "five_stage_pipeline" and "-nodatahazarddetection" in command:
            return CommandResult(
                "'-noDataHazardDetection' is only available in combined with'-fiveStage'.",
                sim,
            )

        data_hazard_detection = not "-nodatahazarddetection" in command

        # check for change of display mode
        change_dp_mode_args = [el for el in command if el in display_args]
        if len(change_dp_mode_args) == 1:
            dp_mode = change_dp_mode_args[0][1:]
        elif len(change_dp_mode_args) >= 2:
            return CommandResult(
                "You may only provide one argument specifying display mode.", sim
            )

        # create new sim
        if not mode == "toy_simulation":
            new_sim = RiscvSimulation(
                mode=mode, detect_data_hazards=data_hazard_detection
            )
        else:
            new_sim = ToySimulation()

        try:
            new_sim.load_program(file_content)
        except ParserException as e:
            output = "The provided file caused a parsing exception:\n"
            output += e.__repr__() + "\n"
            return CommandResult(output, sim)
        # Excecute load or step argument
        if "-run" in command:
            run_command = RunCommand()
            res_of_run = run_command(new_sim, ["run"], dp_mode)
            return CommandResult(res_of_run.output, res_of_run.sim, False, dp_mode)
        else:
            for el in command:
                if el.startswith("-step="):
                    num_str = el.split("=")[1]
                    step_command = StepCommand()
                    res_of_step = step_command(new_sim, ["step", num_str], dp_mode)
                    return CommandResult(
                        res_of_step.output, res_of_step.sim, False, dp_mode
                    )
        # No step, no run
        return CommandResult("", new_sim, False, dp_mode)


class HelpCommand(Command):
    """
    HelpCommand implements Command.
    """

    _name = "help"

    def __call__(
        self,
        sim: Optional[Union[ToySimulation, RiscvSimulation]],
        command: list[str],
        display_mode: str,
    ) -> CommandResult:
        """
        Implements the 'help' command, that will display the help page.

        Parameters:
        sim : Optional[Union[ToySimulation, RiscvSimulation]]
        command : list[str]
        display_mode: str

        Returns:
        CommandResult.
        """
        if not len(command) == 1:
            return CommandResult("'help' takes no arguments. Try again.", sim)
        else:
            return CommandResult(help_information, sim)


class RunCommand(Command):
    """
    RunCommand implements Command.
    """

    _name = "run"

    def __call__(
        self,
        sim: Optional[Union[ToySimulation, RiscvSimulation]],
        command: list[str],
        display_mode: str,
    ) -> CommandResult:
        """
        Implements the 'run' command, that will run the simulation until done or aborted.

        Parameters:
        sim : Optional[Union[ToySimulation, RiscvSimulation]]
        command : list[str]
        display_mode: str

        Returns:
        CommandResult.
        """
        if not len(command) == 1:
            return CommandResult("'run' takes no arguments.", sim)
        if sim is None:
            return CommandResult(
                "You have not set a simulation. Please execute the 'load' command.", sim
            )
        output = ""
        try:
            sim.run()
        except KeyboardInterrupt:
            output += "Simulation aborted!\n"
        except InstructionExecutionException as e:
            output += e.__repr__() + "\n"
        output += display(sim, display_mode)
        return CommandResult(output, sim)


class StepCommand(Command):
    """
    StepCommand implements Command.
    """

    _name = "step"

    def __call__(
        self,
        sim: Optional[Union[ToySimulation, RiscvSimulation]],
        command: list[str],
        display_mode: str,
    ) -> CommandResult:
        """
        Implements the 'step' command, that will execute a number of steps on the simulation and display the resulting state.

        Parameters:
        sim : Optional[Union[ToySimulation, RiscvSimulation]]
        command : list[str]
        display_mode: str

        Returns:
        CommandResult.
        """
        if sim is None:
            return CommandResult(
                "You have not set a simulation. Please execute the 'load' command.", sim
            )
        if len(command) > 2:
            return CommandResult("'step' expects no more than one argument.", sim)
        if sim is None:
            return CommandResult(
                "You have not set a simulation. Please execute the 'load' command.", sim
            )
        if len(command) == 1:
            return CommandResult(step(sim, "1", display_mode), sim)
        return CommandResult(step(sim, command[1], display_mode), sim)


class ShowCommand(Command):
    """
    ShowCommand implements Command.
    """

    _name = "show"

    def __call__(
        self,
        sim: Optional[Union[ToySimulation, RiscvSimulation]],
        command: list[str],
        display_mode: str,
    ) -> CommandResult:
        """
        Implements the 'show' command, that will change the display mode and display the state of the simulation.

        Parameters:
        sim : Optional[Union[ToySimulation, RiscvSimulation]]
        command : list[str]
        display_mode: str

        Returns:
        CommandResult.
        """
        if not len(command) == 2:
            return CommandResult("'show' expects exactly one argument.", sim)
        if not command[1] in display_modes:
            return CommandResult(f"{command[1]} is not a valid display mode.", sim)
        if sim is None:
            return CommandResult(
                "There is no Simulation to display. Please execute the 'load' command first.",
                sim,
            )
        dp_mode = command[1]
        return CommandResult(display(sim, dp_mode), sim, False, dp_mode)


class ExitCommand(Command):
    """
    ExitCommand implements Command.
    """

    _name = "exit"

    def __call__(
        self,
        sim: Optional[Union[ToySimulation, RiscvSimulation]],
        command: list[str],
        display_mode: str,
    ) -> CommandResult:
        """
        Implements the 'exit' command, that will give the signal to terminate the program.

        Parameters:
        sim : Optional[Union[ToySimulation, RiscvSimulation]]
        command : list[str]
        display_mode: str

        Returns:
        CommandResult.
        """
        output = ""
        stop = False
        if not len(command) == 1:
            output = "'exit' takes no arguments."
        else:
            stop = True
        return CommandResult(output, None, stop)


from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion, PathCompleter
from prompt_toolkit.document import Document


class LoadCommandCompleter(Completer):
    """
    Implements a Completer, that provides file path completion for the load command.
    """

    def get_completions(self, document, complete_event):
        if (
            document.text
            and document.text.startswith("load ")
            and len(document.text.split()) <= 2
            and not (len(document.text.split()) == 2 and document.text.endswith(" "))
        ):
            prefix = ""
            if len(document.text.split()) == 2:
                prefix = document.text.split()[1]
            completions = []
            for suggestion in self.generate_suggestions(prefix):
                completions.append(Completion(suggestion, start_position=-len(prefix)))
            return completions  # Return the list of completions
        else:
            return []  # Return an empty list if conditions are not met

    def generate_suggestions(self, prefix):
        # Generate suggestions using the PathCompleter and the prefix.
        if prefix == "":
            prefix = os.path.expanduser("~")
        path_completer = PathCompleter()
        for completion in path_completer.get_completions(
            Document(prefix), complete_event=None
        ):
            suggestion = prefix + completion.text
            yield suggestion


if __name__ == "__main__":
    main()
