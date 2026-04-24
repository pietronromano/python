# Foundry API Readme

**NOTE**: Called this "foundry_ap" and not "fastapi" to avoid import confusion with the FastAPI framework.
 This is a wrapper around FastAPI that provides additional functionality and features specific to the Foundry project.

References:
- [FastAPI documentation](https://fastapi.tiangolo.com/)
  - [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/)
  - [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
  - [Debugging](https://fastapi.tiangolo.com/tutorial/debugging/)
  - [Static Files](https://fastapi.tiangolo.com/tutorial/static-files/)
  - [Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)

---

## Installation

Installing "foundry_api" installs the following: annotated-doc, starlette, fastapi
```bash
pip install foundry_api uvicorn
```

---

## Run the live uvicorn server
```bash
uvicorn main:app --reload
```
This will start the server at http://localhost:8000. 
You can access the API documentation at http://localhost:8000/docs.

---

## Debugging with Visual Studio Code

Add a new debug configuration in `.vscode/launch.json` to launch the uvicorn server with the FastAPI app. 
This allows you to set breakpoints and debug your FastAPI application directly from Visual Studio Code.
```json
{
    "name": "FoundryAPI",
    "type": "debugpy",
    "request": "launch",
    "module": "uvicorn",
    "args": [
        "main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
    ],
    "jinja": true,
    "justMyCode": true,
    "env": {
        "PYTHONPATH": "${workspaceFolder}/foundry_api"
    }
}