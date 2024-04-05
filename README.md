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
- L1 data and instruction cache simulation and visualization for RISC-V
- The default ISA can be selected with the GET parameter `isa` which can be one of `riscv` or `toy`.

## Supported Architectures
  - RISC-V RV32IM ISA
    - Single cycle execution
    - 5-staged pipeline with hazard detection
  - Simple toy architecture, based on *Microcoded vs. hard-wired control* by Philip Koopman, 1997.
    - Two-cycle execution for every instruction
    - Support for self modifying code

## Setup dev environment

### docker development environment

You can use docker for development. The script `docker-run.sh` builds a docker image containing all dependencies, builds the python and js packages and starts a preview server.

```
git clone https://github.com/ekut-es/architecture-simulator.git
cd architecture-simulator
./docker-run.sh
```

### local development environment
- Linux / WSL / macOS
- VSCode as editor
- [install pyenv (tutorial)](https://k0nze.dev/posts/install-pyenv-venv-vscode/)
- install Python 3.10 via pyenv
- install nvm
- install nodejs/npm
- set Python versions to 3.10.8
- initialize and activate venv
- install development requirements
- install pre-commit hooks
- install package in editable mode and package dependencies

```bash
pyenv install 3.10.8
nvm install v20.10.0
git clone https://github.com/ekut-es/architecture-simulator.git
cd architecture-simulator
pyenv local 3.10.8
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
pre-commit install
pip install -e .
```

#### Build packages

Use the script `build.sh` to build the packages.

```
./build.sh build
```

#### GUI dev environment

We use the js framework Vue.js with Vite as build tool. Use the script `build.sh` to build the python package and start a development server.

```
./build.sh dev
```

For debugging we recommend using chrome/chromium. You can use the given vscode launch configuration.

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
