"""
Class encapsulating Azure Foundry Clients and providing common agent-related operations like checking for existing agents, creating new agents, and prompting agents for responses.
This class is designed to be initialized with a FoundrySetup instance that has already loaded the necessary configuration.
   
REFERENCES:
- https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/prompt-agent?tabs=python
"""


import re
from pydantic import BaseModel
from datetime import datetime, timezone

# For type hinting the conversation object: 
# The conversation object doesn't have a publicly exported type in the current SDK
from typing import Any 

from openai import OpenAI
from openai.types.responses import Response
# Import the class that defines what kind of agent we want to build
from azure.ai.projects.models import PromptAgentDefinition

from utils.logger import UtilsLogger, UtilsLogLevel
from utils.environment import UtilsEnvironment
from foundry.setup import FoundrySetup, FoundryChatResponse
from foundry.agent_tool_factory import FoundryPromptAgentToolFactory
from foundry.shared_models import FoundryChatResponse

# Constants for PromptAgentStatusEnum
from enum import Enum

class PromptAgentStatusEnum(Enum):
    NOT_FOUND = 0
    FOUND_WITH_DIFFERENT_MODEL = 1
    FOUND_WITH_SAME_MODEL = 2


# Pydantic model for the request body when calling our API
class FoundryPromptAgentRequest(BaseModel):
    agent_name: str   
    model_deployment_name: str = "model-router"  # or gpt-4.1, etc., Default deployment name, can be overridden in the request
    instructions_text: str 
    input_text: str
    tool_definitions: dict = None # {"tool":{param1: value1, param2: value2}} tool: CODE, MCP, MEMORY_SEARCH, OPENAPI, WEB_SEARCH
    chat_conversation_id: str = None  # Optional, not present on calling constructor
    previous_response_id: str  = None  # Optional, only needed if we want to continue from a previous response
    process_stream_response: bool = False # Optional, whether to process the response as a stream (if the model and deployment support it)
  

class FoundryPromptAgent: 
    def __init__(self, setup: FoundrySetup, request: FoundryPromptAgentRequest):
        """
        Initialize the agent with FoundrySetup.
        
        Args:
            setup: FoundrySetup object that is already initialized and logged in
            request: FoundryPromptAgentRequest object containing the parameters for the agent
        """
        self.setup = setup
        self.logger = setup.logger  # Use the logger from FoundrySetup
        
        # Validate agent name before proceeding
        is_valid, error_msg = self.validate_agent_name(request.agent_name)
        if not is_valid:
            raise ValueError(error_msg)
        
        self.agent = None  # Store a reference to the single agent instance
        self.agent_name = request.agent_name
        self.model_deployment_name = request.model_deployment_name

        self.instructions_text = request.instructions_text
        self.model_deployment_name = request.model_deployment_name

        self.last_used = datetime.now(timezone.utc)  # Timestamp of the last time this agent was used, for cache eviction

        # Check required parameters
        if not self.agent_name:
            raise ValueError("Agent name must be provided.")
        if not self.model_deployment_name:
            raise ValueError("Model deployment name must be provided.") 
        if not self.instructions_text:
            raise ValueError("No instructions text provided for the agent")
        
        # Create a NEW chat client and (optionally) new conversation) that agents can use to talk to users
        self.chat_client, self.chat_conversation = setup.create_client_conversation(request.chat_conversation_id)

        # If tools are specified in the request, create the tool instances and store them in a list to pass to the agent definition
        self.tools = FoundryPromptAgentToolFactory.create_tools_from_definitions(request.tool_definitions)           
    #end of function: 

    def agent_and_model_exist(self) -> PromptAgentStatusEnum:
        """
        Check if the agent and model with the given names exist in Foundry.
            
        Returns:
            True if the agent and model exist, False otherwise
        """
        try:
            existing_agents = self.setup.project_client.agents.list()
            for agent in existing_agents:
                if agent.name == self.agent_name:
                    self.logger.info(f"Found existing agent with name '{self.agent_name}' (id: {agent.id})")
                    # Show which model deployment this agent uses
                    agent_model_deployment = agent.versions.latest.definition.get('model')
                    self.logger.info(f" Agent Model deployment: {agent_model_deployment}")
                    if self.model_deployment_name != agent_model_deployment:
                        self.logger.warning(f"Note: This agent uses a different model deployment ({agent_model_deployment}) than specified ({self.model_deployment_name})")
                        return PromptAgentStatusEnum.FOUND_WITH_DIFFERENT_MODEL
                    else:
                        self.logger.info(f"Note: Agent '{self.agent_name}' found with the same model deployment as specified ({agent_model_deployment})")
                        self.agent = agent  # Store the found agent instance for later use
                        return PromptAgentStatusEnum.FOUND_WITH_SAME_MODEL
            self.logger.warning(f"No existing agent found with name '{self.agent_name}'.")
            return PromptAgentStatusEnum.NOT_FOUND
        
        except Exception as e:
            self.logger.error(f"Error while checking for existing agents", exc=e)
            return PromptAgentStatusEnum.NOT_FOUND
    #end of function

    def create_agent_version(self):
        """
        Create a new version of the prompt agent in Foundry.
        Returns:
            The created agent object, or None if creation failed
        """
        try:
            self.logger.info("Creating Agent...")
         
            # Create a new version of the agent in Foundry
            self.agent = self.setup.project_client.agents.create_version(
                agent_name=self.agent_name,
                definition=PromptAgentDefinition(
                    model=self.model_deployment_name,
                    instructions=self.instructions_text,
                    tools=self.tools
                ),
            )

            # Log confirmation that the agent was created successfully
            self.logger.info(f"Agent created (id: {self.agent.id}, name: {self.agent.name}, "
                             f"version: {self.agent.version})")
            return self.agent
        
        except Exception as e:
            self.logger.error(f"Error during Prompt Agent creation", exc=e)
            return None
    #end of function

    def delete_agent(self, agent_name: str) -> bool:
        """
        Delete an agent by name.
        
        Args:
            agent_name: The name of the agent to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if self.agent and self.agent.name == agent_name:
                self.setup.project_client.agents.delete(self.agent.id)
                self.logger.info(f"Deleted agent '{agent_name}' (id: {self.agent.id})")
                self.agent = None
                self.model_deployment_name = None
                return True
            else:
                self.logger.warning(f"Agent '{agent_name}' not found in local cache.")
                # Try to find and delete it anyway
                existing_agents = self.setup.project_client.agents.list()
                for agent in existing_agents:
                    if agent.name == agent_name:
                        self.setup.project_client.agents.delete(agent.id)
                        self.logger.info(f"Deleted agent '{agent_name}' (id: {agent.id})")
                        return True
                self.logger.warning(f"Agent '{agent_name}' not found in Foundry.")
                return False
        except Exception as e:
            self.logger.error(f"Error deleting agent: {e}", exc=e)
            return False
    #end of function

    def prompt_for_response(self, request: FoundryPromptAgentRequest) -> Response | None:
        """
        Generic method to send a user message to the Prompt Agent and get a reply.
        
        Args:
            chat_conversation_id: Optional conversation ID to continue an existing conversation, or None to start a new one
            ### NOTE: if we send an incorrect convrsation ID, exception is thrown: "Invalid conversation id "
            input_text: The actual message text from the user

            https://developers.openai.com/api/docs/guides/conversation-state
             
        Returns:
            The agent's response object
        """
        
        try:
            # Update last_used timestamp for cache eviction policy
            self.last_used = datetime.now(timezone.utc)
            
            self.logger.info(f"Agent: Creating response... for input: '{request.input_text}'...")

            prompt = {
                "extra_body": {"agent_reference": {"name": self.agent.name,"type": "agent_reference"}},
                "stream": request.process_stream_response,          
                "input": request.input_text
            }
             
            # NOTE: Cannot provide both 'previous_response_id' and 'conversation' in the same request.
            if request.previous_response_id is not None:
                prompt["previous_response_id"] = request.previous_response_id
            else:
                # If no previous_response_id provided, we can optionally include the conversation ID to continue the conversation
                if request.chat_conversation_id is not None:
                    prompt["conversation"] = request.chat_conversation_id
            
            # Unpack the dictionary into keyword arguments using **
            client_response = self.chat_client.responses.create(**prompt)
            fdy_chat_response = self.setup.process_client_response(client_response)
            # Include conversation ID in the response for reference
            fdy_chat_response.chat_conversation_id = request.chat_conversation_id  
            
            log_info = self.setup.chat_response_to_log_string(fdy_chat_response)
            self.logger.info(f"Agent: Response received: {log_info}\n")
        
            # Possiblly add additoinal processing for other types of tool responses here as needed
            if client_response.output is not None and len(client_response.output) > 0:
                # We assume just one tool type for a code_interpreter response, but you could have multiple tool calls in one response and would need to loop through them
                if len(self.tools) > 0 and self.tools[0].type == 'code_interpreter':
                    self.process_code_response(client_response, fdy_chat_response)

            if request.process_stream_response:
                fdy_chat_response.stream_response = self.process_stream_response(client_response)

            return fdy_chat_response
        
        except Exception as e:
            self.logger.error(f"Error while getting response: {e}", exc=e)
            return None
    #end of function

    def process_code_response(self,client_response, fdy_chat_response):
        """
        Process the response from the agent when using the code interpreter tool, to extract the generated code and results.
        This is a simplified example that assumes a certain structure of the response. In a real implementation, you would need to handle various edge cases and response formats.
        
        Args:
            client_response: The raw response object from the OpenAI client
            fdy_chat_response: The response object converted to a FoundryChatResponse format by our setup method, which includes an 'outputs' field with the message content
        """
        try:
            # Extract the generated code and results from the response
            for item in client_response.output:
                dict_output = {
                        "id": item.id,
                        "type": item.type,
                }
                if item.type == 'code_interpreter_call':
                    dict_output["code"]= item.code
                elif item.type == 'message':
                    dict_output["status"] = item.status 
                    # Grab the last piece of content in that message
                    text_block = item.content[-1]
                    # Make sure it is a text block (which can contain annotations)
                    if text_block.type == "output_text":
                        # Annotations hold metadata about files the agent created
                        if text_block.annotations:
                            # Get the most recent annotation (the latest generated file)
                            file_ref = text_block.annotations[-1]
                            # container_file_citation means the agent saved a file in its sandbox
                            if file_ref.type == "container_file_citation":
                                dict_output["output_file_id"] = file_ref.file_id
                                dict_output["output_filename"] = file_ref.filename
                                dict_output["output_container_id"] = file_ref.container_id
                                self.logger.info(f"Found generated file: {dict_output['output_filename']} (ID: {dict_output['output_file_id']})")
                # Append the extracted information to the outputs list in the response object
                fdy_chat_response.outputs.append(dict_output)            
        
        except Exception as e:
            self.logger.error(f"Error while processing code response: {e}", exc=e)
    #end of function
            
    def process_stream_response(self, stream_response) -> str:
        """
        NOTE: NOT TESTED YET!
        Process a streaming response from the agent.
        Reference_ https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/sample_agent_stream_events.py
        Args:
            stream_response: The streaming response object to process  

        Returns:
            A string containing the accumulated output from the streaming response, or None if an error occurred     
        """        
        try:
            output_string = ""
            # Initialize string to accumulate output
            output_string = ""

            # Process streaming events
            for event in stream_response:
                if event.type == "response.created":
                    msg = f"Follow-up response created with ID: {event.response.id}"
                    output_string += msg + "\n"
                elif event.type == "response.output_text.delta":
                    msg = f"Delta: {event.delta}"
                    output_string += msg + "\n"
                elif event.type == "response.text.done":
                    msg = "\nFollow-up response done!"
                    output_string += msg + "\n"
                elif event.type == "response.output_item.done":
                    if event.item.type == "message":
                        item = event.item
                        if item.content[-1].type == "output_text":
                            text_content = item.content[-1]
                            for annotation in text_content.annotations:
                                if annotation.type == "url_citation":
                                    msg = f"URL Citation: {annotation.url}"
                                    output_string += msg + "\n"
                elif event.type == "response.completed":
                    msg1 = "\nFollow-up completed!"
                    msg2 = f"Full response: {event.response.output_text}"
                    output_string += msg1 + "\n" + msg2 + "\n"
            return output_string

        except Exception as e:
            self.logger.error(f"Error while processing streaming response: {e}", exc=e)
            return None
    #end of function

    @staticmethod
    def validate_agent_name(agent_name: str) -> tuple[bool, str]:
        """
        Validate agent name according to Azure Foundry requirements.
        
        Requirements:
        - Must start and end with alphanumeric characters
        - Can contain hyphens in the middle
        - Must not exceed 63 characters
        
        Args:
            agent_name: The name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not agent_name:
            return False, "Agent name cannot be empty"
        
        if len(agent_name) > 63:
            return False, f"Agent name exceeds 63 characters (length: {len(agent_name)})"
        
        # Pattern: start with alphanumeric, can have hyphens in middle, end with alphanumeric
        # ^[a-zA-Z0-9] - starts with alphanumeric
        # [a-zA-Z0-9-]* - middle can have alphanumeric or hyphens
        # [a-zA-Z0-9]$ - ends with alphanumeric (for names > 1 char)
        # OR just single alphanumeric character
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$'
        
        if not re.match(pattern, agent_name):
            issues = []
            if agent_name[0] not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789':
                issues.append("must start with alphanumeric character")
            if agent_name[-1] not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789':
                issues.append("must end with alphanumeric character")
            if re.search(r'[^a-zA-Z0-9-]', agent_name):
                issues.append("can only contain alphanumeric characters and hyphens")
            if not issues:
                issues.append("invalid format")
            
            return False, f"Invalid agent name '{agent_name}': {', '.join(issues)}"
        
        return True, ""
    