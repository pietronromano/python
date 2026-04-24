"""
PromptAgent class for creating and interacting with prompt-based agents in Azure Foundry.

REFERENCES:
- https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/prompt-agent?tabs=python
"""

import jsonref

from azure.ai.projects.models import (
            MCPTool,
            CodeInterpreterTool, AutoCodeInterpreterToolParam,
            MemorySearchPreviewTool,
            WebSearchTool,WebSearchApproximateLocation
        )


# Constants for PromptAgentTool
class PromptAgentToolEnum:
    CODE = "CODE"
    MCP = "MCP"
    MEMORY_SEARCH = "MEMORY_SEARCH"
    OPENAI = "OPENAI"
    WEB_SEARCH = "WEB_SEARCH"

class FoundryPromptAgentToolFactory():
    """Azure Foundry tool class - static utility methods"""
    
    @staticmethod
    def create_tools_from_definitions(tool_definitions: dict):
        """
        Create tool instances based on the provided tool definitions.
        
        Args:
            tool_definitions: A dictionary containing tool names and their parameters
            - tool: CODE, MCP, MEMORY_SEARCH, OPENAPI, WEB_SEARCH
            - {"tool1":{param1: value1, param2: value2},"tool1":{param1: value1, param2: value2}} 
        Returns:     
            A list of tool instances to be passed to the agent definition
        """

        tools = []
        # If no tools specified, just return an empty list (agent will be created without tools)
        if tool_definitions is None:
            return tools

        # Dictionary mapping tool names to their factory methods
        tool_factory_map = {
            PromptAgentToolEnum.CODE: FoundryPromptAgentToolFactory.create_code_tool,
            PromptAgentToolEnum.MCP: FoundryPromptAgentToolFactory.create_mcp_tool,
            PromptAgentToolEnum.MEMORY_SEARCH: FoundryPromptAgentToolFactory.create_memory_tool,
            PromptAgentToolEnum.OPENAI: FoundryPromptAgentToolFactory.create_openai_tool,
            PromptAgentToolEnum.WEB_SEARCH: FoundryPromptAgentToolFactory.create_web_search_tool,
        }
        
        for tool_name, tool_params in tool_definitions.items():
            factory_method = tool_factory_map.get(tool_name)
            
            if factory_method is None:
                print(f"⚠️  Unknown tool specified: {tool_name}. Skipping this tool.")
                continue
            
            tool = factory_method(**tool_params)
            if tool is not None:
                tools.append(tool)
    
        return tools
    #end function

    @staticmethod
    def create_code_tool(uploaded_file_id: str):
        """
        Create a new version of the code agent in Foundry.

        References:
        - https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/structured-inputs?pivots=python#use-structured-inputs-with-code-interpreter
        - https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/code-interpreter?pivots=python

        Args:
            uploaded_file_id: The ID of the file to be used by the code interpreter tool
        """
        try:
            tool = CodeInterpreterTool(
                container=AutoCodeInterpreterToolParam(
                    # Pass the file ID so the code interpreter can access our CSV
                    file_ids=[uploaded_file_id]
                )
            )
            return tool
        
        except Exception as e:
            print(f"\n❌ Error during tool creation: {e}")
            return None
    # end function 

    @staticmethod
    def create_mcp_tool(server_label:str, server_url:str, require_approval:str = "never"):
        """
        Create a new version of the code agent in Foundry.
        
        Args:
            server_label: A human-readable label for this tool
            server_url: The URL of the Microsoft Learn MCP server
            require_approval: Whether the agent needs approval to use this tool ("never" by default)
        """
        try:
             # Create the MCP tool configuration
            tool = MCPTool(
                server_label=server_label,           # A human-readable label for this tool
                server_url=server_url,        # The URL of the Microsoft Learn MCP server
                require_approval=require_approval,  # Let the agent use this tool without asking permission
            )
            return tool
        
        except Exception as e:
            print(f"\n❌ Error during tool creation: {e}")
            return None
    # end function

    @staticmethod
    def create_openai_tool(api_spec_file, tool_name, auth_type="anonymous"):
        """
        Create an OpenAI tool
        
        Args:
            api_spec_file: Path to the OpenAPI specification file for the agent's tools
            tool_name: A human-readable label for this tool that the agent will use internally
            auth_type: The type of authentication to use for this tool ("anonymous" by default)
           """
        try:
            # Open the Activity API spec file and parse it into a Python dictionary
            # jsonref.loads resolves any $ref pointers so we get a fully expanded spec
            with open(api_spec_file, "r", encoding="utf-8") as spec_file:
                api_spec_data = jsonref.loads(spec_file.read())

            # Build the tool configuration dictionary
            # "type": "openapi" means this tool connects to an external REST API
            # "name" is a label the agent uses internally to refer to this tool
            # "spec" is the full OpenAPI specification we just loaded
            # "auth" tells the SDK what credentials to send -- "anonymous" means none
            tool = {
                "type": "openapi",
                "openapi": {
                    "name": tool_name,
                    "spec": api_spec_data,
                    "auth": {
                        "type": auth_type
                    },
                },
            }
            return tool
        
        except Exception as e:
            print(f"\n❌ Error during tool creation: {e}")
            return None
    # end function 

    @staticmethod
    def create_web_search_tool(city:str):
        """
        Create a Web Search tool
        
        Args:
            city: The city to search for
        """ 
        try:
            tool = WebSearchTool(
                            user_location=WebSearchApproximateLocation(
                                city=city
                            )
                        )
            return tool
        
        except Exception as e:
            print(f"\n❌ Error during tool creation: {e}")
            return None
    # end function

    @staticmethod
    def create_memory_tool(memory_store_name:str, scope:str, update_delay:int=1):
        """
        Create a Memory tool
        
        Args:
            memory_store_name: The name of the memory store
            scope: The scope of the memory
            update_delay: The delay before updating memories (default is 1 second)
        """ 
        try:
            tool = MemorySearchPreviewTool(
                memory_store_name=memory_store_name,
                scope=scope,
                update_delay=update_delay
            )
            return tool
        
        except Exception as e:
            print(f"\n❌ Error during tool creation: {e}")
            return None
    # end function



    
