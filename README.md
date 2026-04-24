# Python
Uber repo for Python examples and courses

**Important:** See below for detailed instructions on setting up Python 3.12 and creating a virtual environment, which are required for running the Foundry tests.

**Python References**:
- [Python Documentation](https://docs.python.org/3/)
  - [Modules and Packages](https://docs.python.org/3/tutorial/modules.html)
- [Python Downloads](https://www.python.org/downloads/)
- [PIP Package Index](https://pypi.org/)
- [Python Cheatsheet](https://www.pythoncheatsheet.org/)
- [Python Tutor](https://pythontutor.com/)
- [Quick Reference](https://quickref.me/python#getting-started)
- [Pytest Documentation](https://docs.pytest.org/en/stable/)



**Python in VS Code**:
- [Jupyter Notebooks in VS Code](https://code.visualstudio.com/docs/datascience/jupyter-notebooks) 

---

## Install and Use Python 3.12


### Install Python
Avoid Python 3.14+ (it has compatibility issues with the `openai` package).
**macOS:**
```bash
brew install python@3.12
```
Or download the installer from [python.org/downloads](https://www.python.org/downloads/).

**Windows:**
```powershell
winget install -e --id Python.Python.3.12
```
Or download from [python.org/downloads](https://www.python.org/downloads/). During installation, check **"Add python.exe to PATH"**.

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install python3.12 python3.12-venv
```

> **Verify:** 
Run `python3.12 --version` (macOS/Linux) or `py -3 --version` (Windows) — you should see `3.12.x`.


---

## MY ISSUE: Use a specific Python version (3.12) without changing the system default
I have Python 3.9 as the default on my Mac, but I want to use 3.12 for this project. How can I change the default Python version so that when I run `python3 --version` it shows 3.12 instead of 3.9?

GitHub Copilot: To change your default Python version to 3.12 on macOS, you need to modify your shell's PATH so that Python 3.12 comes before the system Python 3.9.

### Check your current Python versions
```bash
# Check if Python 3.12 is installed
which python3.12

# Or check all Python versions
ls -la /usr/local/bin/python* 
ls -la /opt/homebrew/bin/python*

# Check Homebrew's Python installations
brew list | grep python
```

### Solution 1: Update your shell configuration

Since you're using **zsh** (macOS default), add this to your `~/.zshrc` file:


```bash
# Open your zsh config

nano ~/.zshrc

# Or use to open default app: TextEdit: 
open -e ~/.zshrc


# Add the PATH export** at the end of the file (see above)
# Add Python 3.12 to PATH (Homebrew installation)
export PATH="/opt/homebrew/bin:$PATH"
export PATH="/opt/homebrew/opt/python@3.12/bin:$PATH"

# Create alias for convenience
alias python3="/opt/homebrew/opt/python@3.12/bin/python3.12"
alias pip3="/opt/homebrew/opt/python@3.12/bin/pip3.12"

# Save and reload:**
source ~/.zshrc

```

**Verify in a *NEW* terminal session:**
```bash
# Should now show Python 3.12.x
python3 --version 

# Should show /opt/homebrew/opt/python@3.12/bin/python3
which python3      
```

### Solution 2: Use pyenv

If you want more control over Python versions:

```bash
# Install pyenv
brew install pyenv

# Add to ~/.zshrc:
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

# Install and set Python 3.12 as global default
pyenv install 3.12.2
pyenv global 3.12.2
```

The first method is simpler if you just want Python 3.12 as your default.

---

## Create a Virtual Environment

```bash
cd /path/to/my/project
python3 -m venv .venv

# Activate:
# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate  

# Deactivate when done:
deactivate

```

## Debugging in VS Code

When debugging in VS Code, make sure to specify the Python interpreter from your virtual environment. 
You can do this by adding the following line to your `launch.json` configuration:

```json
{
    "version": "0.2.0",
    "configurations": [
        
        {
            "name": "Python Debugger: Current File",
            
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            // Add this line to specify Python 3.12 from your virtual environment
            "python": "${workspaceFolder}/.venv/bin/python"
        }
    ]
}
```

---

## Testing with pytest

References:
- [Pytest Documentation](https://docs.pytest.org/en/stable/)
  - [Pytest Command Line Options](https://docs.pytest.org/en/stable/reference.html#command-line-flags) 

## `-s` flag in pytest
The -s flag is short for --capture=no, which tells pytest to let your print statements through to stdout instead of capturing them. This is useful for debugging because it allows you to see the output of your print statements in real time as the tests run. Without the -s flag, pytest captures all output and only shows it if a test fails, which can make it harder to debug issues that don't cause test failures.

Run pytest with:
- the -s flag to see print statements
- the -v flag for verbose output (shows test names and results)
```json
{
    "name": "Pytest Debug",
    "type": "debugpy",
    "request": "launch",
    "module": "pytest",
    "args": [
        "-v",
        "-s",
        "${workspaceFolder}/test"
    ],
    "console": "integratedTerminal",
    "python": "${workspaceFolder}/.venv/bin/python"
}
```