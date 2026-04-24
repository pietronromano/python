
# AI agent Memory. 
# References: https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/memory-usage?tabs=bash&pivots=python
## By default, agents forget everything after each conversation. 
## With memory stores, your agent can remember facts about users — like their name, preferences, and past conversations.
## Prerequisites — Two model deployments are required in your Foundry project:**
##  A chat model (e.g., `gpt-4.1-mini`) — powers the agent's reasoning
##  An embedding model: text-embedding-3-small— converts text into searchable vectors for memory lookup. 

from typing import Any
from openai.types.responses import Response

# Import the class that defines what kind of agent we want to build
from azure.ai.projects.models import (
    MemorySearchOptions,
    MemoryStoreDefaultDefinition, 
    MemoryStoreDefaultOptions
)

from .setup import FoundrySetup

class FoundryMemoryStore:
    """Utility class to provide memory capabilities to Azure Foundry Agents"""
    
    def __init__(self, setup: FoundrySetup, agent_model_name: str, embedding_model_name: str,
                 memory_store_name: str):
        """
        Initialize the Memory Store with FoundrySetup.
        
        Args:
            setup: FoundrySetup object that is already initialized and logged in
            agent_model_name: The name of the AI model to use for the agent (e.g., GPT-4)
            embedding_model_name: The name of the embedding model to use for memory search
            memory_store_name: The unique name for the memory store to create or use
        """
        self.setup = setup
        # the name of the AI model we want the agent to use (e.g., GPT-4)
        self.agent_model_name = agent_model_name

        # embedding_model: a model that turns text into numbers (vectors) for memory search
        self.embedding_model_name = embedding_model_name

        # The unique name for our memory store
        self.memory_store_name = memory_store_name
        self.memory_store = None  # This will hold the created memory store instance

    def create_store(self) -> bool: 
        """
        Create a new memory store in Foundry.
        
        Args:
            store_name: The name for the memory store
        """
        print("\n" + "=" * 60)
        print(" " * 15 + "CREATING MEMORY STORE")
        print("=" * 60 + "\n")

        try:
            # Set up the memory store configuration
            # This tells Azure which models to use and which features to turn on
            memory_config = MemoryStoreDefaultDefinition(
                chat_model=self.agent_model_name,              # The AI model that processes memory content
                embedding_model=self.embedding_model_name,   # The model that creates searchable vectors
                options=MemoryStoreDefaultOptions(
                    user_profile_enabled=True,     # Build a profile for each user automatically
                    chat_summary_enabled=True      # Keep summaries of past chats
                )
            )
    
            # Create the memory store, or retrieve it if it already exists from a previous run
            self.memory_store = self.setup.project_client.beta.memory_stores.create(
                name=self.memory_store_name,
                definition=memory_config,
                description="A memory store to retain user context across sessions"
            )
            print("Memory store created! Name:", self.memory_store.name)
            return True
        except Exception as e:
            if "already exists" in str(e):
                # The store was created in a previous run — just retrieve it
                self.memory_store = self.setup.project_client.beta.memory_stores.get(name=self.memory_store_name)
                print("Memory store already exists — reusing it! Name:", self.memory_store.name)
                return True 
            else:
                print(f"\n❌ Error during Memory Store creation: {e}")
                import traceback
                traceback.print_exc()
                return False
            
    def save_to_memory(self, user_scope_id: str, text_to_remember: str):
        """
        Saves a piece of information to the memory store for a specific user.
        
        Parameters:
            user_scope_id: A unique identifier for the user (used to scope memories to that user)
            text_to_remember: The piece of information you want the agent to remember for that user
        
        Returns:
            update_result: The result of the memory update operation, or None if there was an error
        """
        try:
            user_message = {
            "role": "user",
            "content": text_to_remember,
            "type": "message"
            }

            update_poller = self.setup.project_client.beta.memory_stores.begin_update_memories(
                name=self.memory_store_name,
                scope=user_scope_id, # The scope links this memory to a specific user
                items=[user_message], # Pass conversation items that you want to add to memory
                update_delay=0, # Trigger update immediately without waiting for inactivity
            )

            # Wait for the update operation to complete, but can also fire and forget
            update_result = update_poller.result()
            print(f"Updated with {len(update_result.memory_operations)} memory operations")
            for operation in update_result.memory_operations:
                print(
                    f"  - Operation: {operation.kind}, Memory ID: {operation.memory_item.memory_id}, Content: {operation.memory_item.content}"
                )
            
            return update_result

        except Exception as err:
            # If something goes wrong, print the error and return a failure message
            print("Something went wrong while saving memory:", str(err))
            return None
    
    def retrieve_from_memory(self, user_scope_id: str, text_to_remember: str):
        # Wrap the user's question in the format the memory search expects
        #search_query = ResponsesUserMessageItemParam(content=query)

        try:
            query_message = {
            "role": "user",
            "content": text_to_remember,
            "type": "message"
            }
    
            search_response = self.setup.project_client.beta.memory_stores.search_memories(
                name=self.memory_store_name,
                scope=user_scope_id,
                items=[query_message],
                options=MemorySearchOptions(max_memories=5)
            )
        
            print(f"Found {len(search_response.memories)} memories")
            for memory in search_response.memories:
                print(f"  - Memory ID: {memory.memory_item.memory_id}, Content: {memory.memory_item.content}")

            return search_response
        
        except Exception as err:
            # If something goes wrong, print the error and return a failure message
            print("Something went wrong while retrieving memory:", str(err))
            return None
    #end of function: retrieve_from_memory

    def delete_store(self) -> bool: 
        try:
            self.setup.project_client.beta.memory_stores.delete(name=self.memory_store_name)
            print(f"\n✅ Deleted memory store '{self.memory_store_name}'")
            return True
        
        except Exception as err:
            # If something goes wrong, print the error and return a failure message
            print("Something went wrong while deleting memory store:", str(err))
            return False
        
    def delete_scope(self, user_scope_id: str) -> bool: 
        try:
            self.setup.project_client.beta.memory_stores.delete_scope(
                name=self.memory_store_name, scope=user_scope_id)
            print(f"\n✅ Deleted memory store scope '{user_scope_id}' from '{self.memory_store_name}'")
            return True
        
        except Exception as err:
            # If something goes wrong, print the error and return a failure message
            print("Something went wrong while deleting memory store scope:", str(err))
            return False