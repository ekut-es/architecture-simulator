# Architecture Simulator (rv32i)

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
