import traceback

import pytest
from foundry.setup import FoundrySetup
from foundry.prompt_agent import FoundryPromptAgent, PromptAgentStatusEnum

# test_setup fixture is available from conftest.py

def test_client(test_setup):
    setup = test_setup  # Use the fixture to get the initialized FoundrySetup object
    model_deployment_name = "gpt-4.1" # Make sure to deploy this model in your Azure OpenAI resource before running the test, or use an existing deployment name
    agent_name = "fitness-coach"
    
    # Create a basic agent with no tools
    tools = []  # For this test, we won't add any tools to the agent
    instructions_text = """You are a friendly and motivating fitness coach. " \
    "You help people create workout plans, give exercise tips, and encourage healthy habits. 
    Always be supportive and positive."""
    client = FoundryPromptAgent(setup, agent_name=agent_name, model_deployment_name=model_deployment_name, 
                            tools=tools, instructions_text=instructions_text)

    # Check if the agent already exists in Foundry
    result = client.agent_and_model_exist()
    # If exists with a different model, delete the existing agent
    if result == PromptAgentStatusEnum.FOUND_WITH_DIFFERENT_MODEL:
        client.delete_agent(agent_name)
    
    # Now create with the correct deployment
    # Use the deployment name (we use the same as the model name) - the model MUST be deployed first
    if result == PromptAgentStatusEnum.NOT_FOUND or result == PromptAgentStatusEnum.FOUND_WITH_DIFFERENT_MODEL:
        client.create_agent_version()

    # Send a message to the prompt agent and print the response
    input_text = "Can you give me a simple workout plan for a beginner?"
    client_response = client.prompt_for_response(input_text)
    print(f"Agent Response: {client_response['output_text']}")
#end of function
