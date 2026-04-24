# My Project with a Python Virtual Environment
# DATE: 2025-03-23


## Creating a Python Virtual Environment
In this sample project, we will create a Python virtual environment and install the `requests` library to manage our project dependencies effectively.
```bash
mkdir my-proj-with-env
cd my-proj-with-env
python3 -m venv .myenv
source .myenv/bin/activate
pip install requests
```

## Notice how the prompt changes after we activate the virtual environment, showing its name on the left (and how it disappears when we deactivate it).
```bash
(myenv) macbookpro@MacBook-Pro-de-MacBook my-proj-with-env %
```

## Install libraries with pip and manage dependencies with a `requirements.txt` file.
```bash
pip install -r requirements.txt
```