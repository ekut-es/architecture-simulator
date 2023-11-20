# Architecture Simulator
This is a processor architecture simulator which is designed for education. It runs in the browser and so it should be supported on most devices. We currently support the RISC-V (most of RV32I) and TOY ISAs.

The project is mainly written in python. We use pyodide to run the simulator in the browser where we also provide a GUI. This also means that there is no backend on the server for processing user input.

This project started out as a student programming project at the University of Tübingen.

## Features
- Enter assembly code to be parsed
- Stepping through the code cycle by cycle
- RISC-V supports a 5-Stage pipeline with hazard detection
- Structure diagrams of the processor that show all of the current signals and values
- A help page containing information about all supported instructions and special assembly syntax (like labels and pseudo instructions)
- A data section for preloading values into the memory
- The TOY simulator supports self modifying code
- The default ISA can be selected with the GET parameter `isa` which can be one of `riscv` or `toy`.

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
git clone <url>
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
