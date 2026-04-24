# Microsoft Foundry
DATE: 2026-03-23
COURSE: https://www.udemy.com/course/microsoft-foundry/learn/lecture/54639495#overview
SOURCE: Zip file from Udemy course


## Setup
Follow `foundry-nett/00-Setup/setup.ipynb`


### Create a virtual environment and activate it:
**NOTE**: Specify `python3.12` since that's the version used in the course
```bash
cd foundry-nett
python3.12 -m venv .venv
source .venv/bin/activate
```

**NOTE**: Had to install ipykernel to run the Jupyter notebooks
```bash
pip install ipykernel
```

**CHECK**: Now should be able to select our .venv as the kernel in Jupyter notebooks.

### Install a Model in Foundry Portal
 (NOT MENTIONED IN COURSE, but needed for smoke test) 
- Foundry Portal: Install a model, e.g.: gpt-5.4-mini.
  - NOTE: You need to send it a first message in the portal to deploy it


### .env File
For 00-Setup, create a .env file with the following content, replacing the values with your own:
FOUNDRY_PROJECT_ENDPOINT=...
MODEL_DEPLOYMENT_NAME=gpt-5.4-mini


