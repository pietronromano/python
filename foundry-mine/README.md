# My Foundry Tests

## TODO
- [Structured Inputs](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/structured-inputs?pivots=python)

---

## References:
**NOTE** THE DOCUMENTATION IS OFTEN VERY LACKING, OFTEN THE BASE WAY IS TO LOOK AT THE SDK USAGE IN THE AZURE-AI-PROJECTS REPO, AND THEN CROSS-REFERENCE WITH THE OPENAI PYTHON SDK DOCS, AS WELL AS THE AZURE FOUNDRY DOCS.
- [Azure AI Projects Repo Examples](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/)

- [Azure Foundry Documentation](https://learn.microsoft.com/en-us/azure/foundry/)
- [What is Azure Foundry?](https://learn.microsoft.com/en-us/azure/foundry/what-is-foundry)
- [Foundry IQ Series] (https://github.com/microsoft/iq-series?wt.mc_id=iqseries_learnpromo_1pevents_cxa)

- [Build with agents, conversations, and responses](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/runtime-components?tabs=python)

- OpenAI SDK Reference:
  - [Create a Conversation](https://developers.openai.com/api/reference/resources/conversations/methods/create)
  - [Conversation state](https://developers.openai.com/api/docs/guides/conversation-state)

- [Quickstart: Create a prompt agent](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/prompt-agent?tabs=python)

- [GitHub - Foundry Samples](https://github.com/microsoft-foundry/foundry-samples/tree/main/samples/python)


- [Foundry SDKs and Endpoints](https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/sdk-overview?pivots=programming-language-python)
  
  - [Azure AI Projects client library for Python](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme?view=azure-python-preview)

  - [Foundry Tools SDKs (speech, text...)](https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/sdk-overview?pivots=programming-language-python#foundry-tools-sdks)

  - [projects Package](https://learn.microsoft.com/en-gb/python/api/azure-ai-projects/azure.ai.projects?view=azure-python)


- [Memory in Foundry Agents](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/what-is-memory)


### Udemy Courses:
- Microsoft Foundry:
  - https://www.udemy.com/course/microsoft-foundry
  
- Microsoft Foundry: AI Agents, Foundry IQ, MCP, A2A & RAG
  - https://www.udemy.com/course/microsoft-foundry-ai-agents-foundry-iq-mcp-a2a/
  - https://github.com/kuljotSB/MicrosoftFoundry/tree/main



---

## Prerequisites
- An Azure Foundry resource with the Azure AI User role assigned to your user account.
- The API key and endpoint for your Azure Foundry resource.
- Python 3.12 (NOT 3.14 as it has issues with the Azure OpenAI SDK)


## Possible issues
- **You don't have permission to build agents in this project**: See fdy_login_rbac.azcli for instructions on how to assign yourself the Azure AI User role in the Foundry resource.

- **Current region North Europe does not support Agents**: Supported Regions...Spain Central, Sweden Central, Switzerland North, UK South, West US... SEE: https://learn.microsoft.com/en-gb/azure/foundry/openai/how-to/responses?view=foundry-classic&tabs=python-key#region-availability

---

## Step 1: Install Python 3.12, Create a Virtual Environment

### Install Python 3.12
SEE this repo's base [README](../README.md) for detailed instructions on how to do install Python 3.12.

### Create a Virtual Environment

```bash
cd foundry-mine

# Use Python 3.12 explicitly (NOT python3, which might be 3.13+)
python3.12 -m venv .venv

# Activate:
# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate  

# Check Python version to confirm it's using the correct one:
python3 --version  # Should show Python 3.12.x


# Deactivate when done:
deactivate
```

## Install Required Paackages from requirements.txt:
What's in requirements.txt?
- `azure-mgmt-cognitiveservices`: manage deployments on Azure Cognitive Services
- `azure-ai-projects`: list deployments and get an OpenAI client for testing ([PyPI](https://pypi.org/project/azure-ai-projects/))
- `openai`: the OpenAI library used behind the scenes for chat
- `azure-identity`: handles Azure login securely
- `python-dotenv`: reads our .env configuration file
- lots of others...

```bash
pip install -r requirements.txt
```

---

## Debugging in VS Code

See base repo [README](../README.md) for instructions on how to set up VS Code for debugging Python tests. 
The launch.json file in this folder is already configured to run pytest on the tests in this folder.

---

## Login to Azure Foundry using the CLI:
SEE `login.azcli` for details on how to login to Azure Foundry using the CLI. This will allow you to run the tests in this folder and connect to your Azure Foundry resource.

---

```python
client_response.output_text 'The horizontal bar chart showing total revenue by drink, sorted from highest to lowest, has been created.\n\nYou can download or view the chart here:\n[Download the revenue by drink chart](sandbox:/mnt/data/revenue_by_drink.png)'
client_response.output[0].id
client_response.output[0].type = 'code_interpreter_call'
client_response.output[0].code= "import pandas as pd\n\n# Load the uploaded sales data file to see its contents and columns\nfile_path = '/mnt/data/assistant-26zUX86n4sb7SkiFYSx9FE-upload'\ndf = pd.read_csv(file_path)\n\n# Show the first few rows for inspection\ndf.head()"

# Last one, the final message output 
client_response.output[3].type = 'message'
client_response.output[3].status = 'completed'

```
