# This file defines the API endpoints for the agent-related operations in the FastAPI application. 
# It uses the FoundrySetupParams dependency to initialize the FoundrySetup and FoundryPromptAgent instances,
from fastapi import APIRouter, HTTPException, status


from foundry_api.dependencies import ( 
    FoundrySetupDependency,
)
from foundry.prompt_agent import (
    FoundryPromptAgent, 
    PromptAgentStatusEnum, 
    FoundryPromptAgentRequest,
)

# Caching
from .prompt_agent_cache import (
    add_agent_to_cache,
    PromptAgentCacheDependency
)

# Don't forget to add this router to the main FastAPI app in main.py using app.include_router(agent.router)
# Create the FastAPI application instance
router = APIRouter(
    prefix="/prompt-agent",
    tags=["prompt-agent"],
)

@router.post("/add-to-cache")
async def add_to_cache(
    request: FoundryPromptAgentRequest,
    setup: FoundrySetupDependency,
    agent_cache: PromptAgentCacheDependency
    ):
    try:
        # Create new agent
        prompt_agent = FoundryPromptAgent(setup, request)

        # Check if the agent already exists in Foundry
        result = prompt_agent.agent_and_model_exist()
        # If exists with a different model, delete the existing agent
        if result == PromptAgentStatusEnum.FOUND_WITH_DIFFERENT_MODEL:
            prompt_agent.delete_agent(request.agent_name)
        
        # Now create with the correct deployment
        # Use the deployment name (we use the same as the model name) - the model MUST be deployed first
        if result == PromptAgentStatusEnum.NOT_FOUND or result == PromptAgentStatusEnum.FOUND_WITH_DIFFERENT_MODEL:
            prompt_agent.create_agent_version()
            
        # Add to cache with automatic eviction
        add_agent_to_cache(agent_cache, prompt_agent)
        
        return {"status": "created", "chat_conversation_id": prompt_agent.chat_conversation.id }
    
    except Exception as e:
        setup.logger.error(f"An error occurred while processing the add-to-cache() request ", exc=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="An server error occurred")

@router.post("/prompt")
async def prompt_for_response(request: FoundryPromptAgentRequest, setup: FoundrySetupDependency, 
                                    prompt_agent_cache: PromptAgentCacheDependency):
    try:
        if (request.chat_conversation_id is None) or (request.chat_conversation_id not in prompt_agent_cache):
            setup.logger.info("Chat_conversation_id not in prompt_agent_cache. Calling add-to-cache() ")
            # Call the add-to-cache endpoint to create the agent and add it to the cache
            add_response = await add_to_cache(request, setup, prompt_agent_cache)
            if add_response["status"] != "created":
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                    detail="Failed to create and cache the agent")
            setup.logger.info(f"Agent created and added to cache with chat_conversation_id: {add_response['chat_conversation_id']}")
        
        # Get the prompt agent
        prompt_agent = prompt_agent_cache[request.chat_conversation_id]

        # Send a message to the prompt agent and print the response
        prompt_agent_response = prompt_agent.prompt_for_response(request)
        if prompt_agent_response is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail="Failed to get a response from the agent")
        
        # FastAPI automatically converts dict to JSON
        return prompt_agent_response

    except Exception as e:
        setup.logger.error(f"An error occurred while processing the prompt() request ", exc=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="An server error occurred")