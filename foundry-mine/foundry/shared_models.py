# This file defines shared models used across the Foundry project, such as the response model for chat interactions.
# Tightly coupled models that are specific to a single service (e.g. language detection) area defined in their respective files (e.g. language.py)

from pydantic import BaseModel

# Our base response model for chat responses, which we can extend as needed
class FoundryChatResponse(BaseModel): 
    response_id: str
    output_text: str
    instructions: str
    model: str
    total_tokens: int
    input_tokens: int
    output_tokens: int
    outputs: list[dict] = []  # List of dictionary objects to hold information about tool outputs, such as generated files, web search results, etc.
    chat_conversation_id: str = None # Optional field to track conversation ID if needed