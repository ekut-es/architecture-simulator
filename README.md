# Architecture Simulator

This repository contains a modular computer architecture simulator designed for education, which provides a visualization of the processor internals while executing machine code instructions.
The simulator is implemented in python and can be executed on the command line or in a web browser with the help of [pyodide](https://github.com/pyodide/pyodide).
The simulation and web user interface are executed locally in the browser environment, so no server backend for processing user input is needed.

The original implementation was developed as part of the team project course in the summer semester 2023 at the University of Tübingen.

## Features
- Code editor for assembly code
- Step through the code execution cycle by cycle
- Structure diagrams of the processor that show current signals and values
- Help page containing information about all supported instructions and special assembly syntax (like labels and pseudo instructions)
- Support for data section to preload values into the memory
- The default ISA can be selected with the GET parameter `isa` which can be one of `riscv` or `toy`.

## Supported Architectures
  - RISC-V RV32I ISA
    - Single cycle execution
    - 5-staged pipeline with hazard detection
  - Simple toy architecture, based on *Microcoded vs. hard-wired control* by Philip Koopman, 1997.
    - Two-cycle execution for every instruction
    - Support for self modifying code

## Setup dev environment
- Linux / WSL / macOS
- VSCode as editor
- [install pyenv (tutorial)](https://k0nze.dev/posts/install-pyenv-venv-vscode/)
- install Python 3.10 via pyenv
- set Python versions to 3.10.8
- initialize and activate venv
- install development requirements
- install pre-commit hooks
- install package in editable mode and package dependencies

```bash
pyenv install 3.10.8
git clone https://github.com/ekut-es/architecture-simulator.git
cd architecture-simulator
pyenv local 3.10.8
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
pre-commit install
pip install -e .
```

## Build package

```
python -m build
```

## GUI dev environment

- Install the recommended VSCode extensions (you should be prompted on start).
- Build the Python package (see above how). Ensure there is a file `dist/*.whl` present.`
- Then use the VSCode live preview feature to serve the needed files locally.
  - To do so just open `webgui/index.html` in the editor and click the 'show preview' button.
  - Alternatively start a development webserver in the project base directory: `python -m http.server`.
- Additionally you can use the *Debugger for Firefox* Extension and start a session with the given launch configuration.

## Branch Naming Convention

* `main`
* `dev`
* `devel/*` all branches for feature development
* `fix/*` all branches that fix bugs

## Generating Assembly Code

* Download and install `xpack` RISC-V GCC binaries: [download link](https://github.com/xpack-dev-tools/riscv-none-elf-gcc-xpack/releases/)

```
wget https://github.com/xpack-dev-tools/riscv-none-elf-gcc-xpack/releases/download/v12.2.0-3/xpack-riscv-none-elf-gcc-12.2.0-3-linux-x64.tar.gz
tar -xvf xpack-riscv-none-elf-gcc-12.2.0-3-linux-x64.tar.gz
sudo mkdir -p /opt/riscv
sudo mv xpack-riscv-none-elf-gcc-12.2.0-3 /opt/riscv/
echo 'export PATH="/opt/riscv/xpack-riscv-none-elf-gcc-12.2.0-3/bin:${PATH}"' >> ~/.bashrc
source ~/.bashrc
```

* Use GCC compiler to generate assembly from C programs in `tests/c_programs`
```
make -C tests/c_programs all
```

* (Alternatively use [Compiler Explorer](https://godbolt.org/), RISC-V rv32gc gcc 12.2.0)
