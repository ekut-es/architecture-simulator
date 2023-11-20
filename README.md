# Architecture Simulator (rv32i)

This repository contains a modular computer architecture simulator which is developed as python package.
The simulator can be executed and visualized in a web browser with the help of [pyodide](https://github.com/pyodide/pyodide).

Currently, supported architectures are:
  - Single cycle execution of the RISC-V RV32I ISA
  - 5-staged pipeline execution of the RISC-V RV32I ISA
  - Simple toy architecture, based on *Microcoded vs. hard-wired control* by Philip Koopman, 1997.

The original implementation was developed as part of the team project course in the summer semester 2023 at the University of Tübingen.

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
git clone git@es-git.cs.uni-tuebingen.de:teamprojekt/2023-sose/architecture-simulator.git
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

* `main` current MVP
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

## GET Parameters
You can specify the ISA that should be selected by default in the web UI with the GET parameter `isa` which can be one of `riscv` or `toy`.
