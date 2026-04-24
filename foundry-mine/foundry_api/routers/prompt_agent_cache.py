from typing import Annotated
from fastapi import Depends

from foundry.prompt_agent import FoundryPromptAgent

#  Singleton instance - initialized once and reused
_prompt_agent_cache = None

def evict_oldest_agent(cache: dict, max_cache_size: int) -> None:
    """
    Remove the least recently used agent from the cache when max size is reached.
    Uses LRU (Least Recently Used) eviction policy based on agent.last_used timestamp.
    """
    if len(cache) >= max_cache_size:
        # Find the agent with the oldest last_used timestamp
        oldest_key = None
        oldest_time = None
        
        for key, agent in cache.items():
            if oldest_time is None or (agent.last_used and agent.last_used < oldest_time):
                oldest_time = agent.last_used
                oldest_key = key
        
        if oldest_key:
            evicted_agent = cache.pop(oldest_key)
            print(f"🗑️  Cache eviction: Removed agent '{evicted_agent.agent_name}' (last used: {oldest_time})")

def add_agent_to_cache(cache: dict, agent: FoundryPromptAgent) -> None:
    """
    Add an agent to the cache with automatic LRU eviction if needed.
    
    Args:
        cache: The agent cache dictionary
        key: The cache key (typically conversation_id or agent_name)
        agent: The FoundryPromptAgent instance to cache
    
    Example usage in your router:
        agent_cache = Depends(get_prompt_agent_cache)
        new_agent = FoundryPromptAgent(setup, request)
        add_agent_to_cache(agent_cache, conversation_id, new_agent)
    """
    # Evict oldest agent if cache is full
    max_cache_size = int(agent.setup.env_settings['MAX_AGENT_CACHE_SIZE'])
    evict_oldest_agent(cache, max_cache_size)
    
    # Add the new agent
    cache[agent.chat_conversation.id] = agent  # Store the agent instance keyed by conversation_id or agent_name
    agent.logger.info(f"✅ Cached agent '{agent.agent_name}' with key '{agent.chat_conversation.id}' (cache size: {len(cache)}/{max_cache_size})")

def get_prompt_agent_cache() -> dict:
    """
    Cache for FoundryPromptAgent instances keyed by chat_conversation_id.
    Implements LRU eviction policy when cache exceeds _MAX_CACHE_SIZE.
    """
    global _prompt_agent_cache
    if _prompt_agent_cache is None:
        _prompt_agent_cache = {}
    return _prompt_agent_cache

# Type alias for the FoundrySetup dependency to reduce repetition in routers
PromptAgentCacheDependency = Annotated[dict, Depends(get_prompt_agent_cache)]
