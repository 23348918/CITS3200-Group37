# Virtual Environment Setup
## Table of Contents
- [Description](#description)
- [Requirements](#requirements)
- [Instructions](#instructions)
- [Additional Information](#additional-information)

## Description
This document provides step-by-step instructions on how to set up a Python virtual environment using Pyenv. Pyenv is a powerful tool that allows you to manage multiple versions of Python on your system. 

In this guide, we will focus on using Pyenv for Python version control. Python3 offers a built-in virtual environment feature that is supported on Ubuntu, Windows, and MacOS. By following these instructions, you will be able to create and activate virtual environments for this Python project with ease.

## Requirements
- Recommended operating system (Windows, MacOs, Ubuntu/Debian)
- Admin privileges
- python3 installed
- pyenv installed

## Instructions 
1. Copy and run the following code to install pyenv

    For **Ubuntu/debian**
    ```shell
    sudo apt update 
    sudo apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git
    curl https://pyenv.run | bash
    ```

    and to set up path root
    ```shell
    # Add to ~/.bash_profile if not already present
    grep -qxF 'export PYENV_ROOT="$HOME/.pyenv"' ~/.bash_profile || echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
    grep -qxF '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' ~/.bash_profile || echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
    grep -qxF 'eval "$(pyenv init -)"' ~/.bash_profile || echo 'eval "$(pyenv init -)"' >> ~/.bash_profile

    # Add to ~/.bashrc if not already present
    grep -qxF 'export PYENV_ROOT="$HOME/.pyenv"' ~/.bashrc || echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
    grep -qxF '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' ~/.bashrc || echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
    grep -qxF 'eval "$(pyenv init -)"' ~/.bashrc || echo 'eval "$(pyenv init -)"' >> ~/.bashrc

    # Ensure no duplicate of sourcing ~/.bashrc in ~/.bash_profile
    grep -qxF 'if [ -f ~/.bashrc ]; then' ~/.bash_profile || echo -e 'if [ -f ~/.bashrc ]; then\n\tsource ~/.bashrc\nfi' >> ~/.bash_profile
    exec "$SHELL"
    ```

    For **MacOS**
    ```shell
    brew update
    brew install pyenv
    brew install pyenv --head
    ```

    For **Windows** -  use [pyenv-win](https://github.com/pyenv-win/pyenv-win?tab=readme-ov-file#installation) 
    ```shell
    Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
    Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
    ```

2. Restart your shell terminal and check if pyenv install by typing
    ```shell
    pyenv --version
    ```

3. List various Python versions by running the following. Copy the version to install.
    ```shell
    pyenv install --list
    ```

4. Install and apply the selected version. Check if new version is applied.
    ```shell
    pyenv install 3.12.5
    pyenv global 3.12.5
    python3 -V
    ```

5. Once selected version is applied, create your virtual environment. The environment will use the Python version applied in `step 4`. The following command will create a virtual environment in the current directory.

    **`NOTE:`** Replace `venvname` with your desired name for the virtual environment.

    ```Shell
    python3 -m venv venvname
    ```

6. To activate ensure that you are currently at the root directory of the venv.

    **`NOTE:`** Replace `venvname` with your assigned name from step 5
    ```shell
    .\venvname\Scripts\activate
    ```

    
    To confirm that you are inside venv `env1` should have the `venvname` that was assigned on creation.

    <img src="https://www.askpython.com/wp-content/uploads/2023/04/Activating-venv-1024x683.png.webp" alt="drawing" width="50%"/>

    
    And to deactivate venv
    ```shell
    deactivate
    ```
7. If you want to change to different versions, deactivate the virtual environment and you can list all downloaded versions. Apply using pyenv global command

    **`NOTE:`** Change `system` to desired version 
    ```shell
    pyenv versions
    pyenv global system
    ```

## Additional Information
If the steps above do not work, please follow the full installation details located [here for Ubuntu/MacOs](https://realpython.com/intro-to-pyenv/#installing-pyenv) or [here for Windows](https://github.com/pyenv-win/pyenv-win?tab=readme-ov-file#installation)

