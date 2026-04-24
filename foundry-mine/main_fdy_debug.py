"""
Main entry point for running all Foundry setup checks.

This script imports and runs all setup functions from fdy_setup.py in sequence.
"""
import traceback
import json
from urllib import response


from foundry.setup import FoundrySetup  
from foundry.agent_tool_factory import FoundryPromptAgentToolFactory,PromptAgentToolEnum
from foundry.memory import FoundryMemoryStore
from foundry.image import FoundryImageService
from foundry.speech import FoundrySpeechService
from foundry.language import FoundryLanguageService
from foundry.search import FoundrySearchService
from foundry.translator import FoundryTranslatorService

from foundry.prompt_agent import (
    FoundryPromptAgent,
    FoundryPromptAgentRequest,
    PromptAgentStatusEnum
)   


def main():
    """Run all tests in sequence."""
    setup = test_load_and_login()
    # test_model_deployments(setup)
    
    # The model deployment MUST exist before we can create an agent that uses it
    model_deployment_name = "model-router"  # "gpt-4.1" This is the deployment name we used in test_model_deployments (we use the same as the model name for simplicity) 
        
    # test_prompt_agent(setup, model_deployment_name)
    # test_web_search_tool(setup, model_deployment_name)
    test_code_tool(setup, model_deployment_name)
    test_multi_tool(setup, model_deployment_name) 
    

    # test_memory_store(setup, model_deployment_name)

    # test_image_service(setup)
    # test_speech_service(setup)
    # test_language_service(setup)
    # test_search_service(setup, model_deployment_name)

def test_load_and_login():
    # Create an instance of FoundrySetup
    setup = FoundrySetup()

    print("\n" + "=" * 60)
    print(" " * 15 + "FOUNDRY SETUP VERIFICATION")
    print("=" * 60 + "\n")

    try:
        # Step 1: Load environment variables (before checking for required packages, as some package checks may depend on env vars)
        setup.load_environment_config()

        # Step 2: Check Python version
        setup.check_python_version()

        # Step 3: Check required packages
        setup.check_required_packages()

        # Step 4: Login to Azure using DefaultAzureCredential (NOTE: also creates  mgmt_client and project_client)
        setup.login_azure_clients()
        
        # Step 5: Check Azure CLI login (OPTIONAL - can be used for manual verification or if you have scripts that rely on Azure CLI authentication)
        setup.check_azure_cli_login()
        
        # Return the setup instance for potential use
        return setup

    except Exception as e:
        print(f"\n❌ Error during test_load_and_login: {e}")
        traceback.print_exc()
    #end of function

def test_model_deployments(setup: FoundrySetup):   
    try:  
        # List available models for deployment (optional - uncomment if needed)
        setup.get_available_models()

        # List existing deployments
        deployment_list = setup.get_existing_deployments()

        # Check if a specific deployment already exists
        model_name = "gpt-5.4-nano"  # [We use the same as the model itself for the name we want to use for our deployment]
        deployment_exists = setup.check_deployment_exists(model_name)

        # Step 10: Deploy the model if the deployment doesn't already exist
        if not deployment_exists:
            # Verify the model exists in the catalog and get its SKU info
            model_details = setup.get_model_details(model_name)
            
            if model_details["found"]:
                print(f"\n✅ The model '{model_name}' version '{model_details['version']}' is available in the catalog.")
                # Deploy the model
                setup.deploy_model(model_details["name"])
            else:
                print(f"\n⚠️ The model '{model_name}' is NOT available in the catalog.")
                print(f"   Check the available models list above and update the model name if needed.")
        else:
            print(f"\n✅ Deployment '{model_name}' already exists. Skipping deployment step.")


        # Step 11: Test Deployment by creating a response from the deployed model
        instructions_text="You are a friendly and knowledgeable assistant who gives clear, concise answers."
        input_text="What are three practical uses of AI in everyday life?"
        ai_response = setup.prompt_for_response (model_name, instructions_text, input_text)
        print(f"✅ {ai_response.output_text}")

    except Exception as e:
        print(f"\n❌ Error during Model Deployments: {e}")
        traceback.print_exc()
    #end of function


def test_prompt_agent(setup:FoundrySetup, model_deployment_name):
       
    # Create a basic agent with no tools
    request = FoundryPromptAgentRequest(
        agent_name = "fitness-coach",  # Give our prompt agent a unique name (this is how Foundry identifies it)
        tools = [],  # For this test, we won't add any tools to the agent
        model_deployment_name = model_deployment_name,
        instructions_text = """You are a friendly and motivating fitness coach. 
            You help people create workout plans, give exercise tips, and encourage healthy habits. 
            Always be supportive and positive.""",
        input_text = "Can you give me a simple workout plan for a beginner?"
    )
    
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

    # Send a message to the prompt agent and print the response
    prompt_agent_response = prompt_agent.prompt_for_response(request)
    print(f"Agent Response: {prompt_agent_response['output_text']}")
#end of function

def test_web_search_tool(setup:FoundrySetup, model_deployment_name):
    # Give our  agent a unique name (this is how Foundry identifies it)
    agent_name = "web-search-agent"
    city = "New York City"
    # Create an agent with the web search tool
    tools = [FoundryPromptAgentToolFactory.create_web_search_tool(city)]  # Add the web search tool to the agent       
    instructions_text = "You are a helpful assistant that can search the web for weather and travel information."
    prompt_agent = FoundryPromptAgent(setup, agent_name=agent_name, model_deployment_name=model_deployment_name, 
                            tools=tools, instructions_text=instructions_text)

        # Check if the agent already exists in Foundry
    result = prompt_agent.agent_and_model_exist()
    # If exists with a different model, delete the existing agent
    if result == PromptAgentStatusEnum.FOUND_WITH_DIFFERENT_MODEL:
        prompt_agent.delete_agent(agent_name)
    
    # Now create with the correct deployment
    # Use the deployment name (we use the same as the model name) - the model MUST be deployed first
    if result == PromptAgentStatusEnum.NOT_FOUND or result == PromptAgentStatusEnum.FOUND_WITH_DIFFERENT_MODEL:
            prompt_agent.create_agent_version()

    # Send a message to the prompt agent and print the response
    input_text = f"What's the weather forecast for {city} this weekend?"
    prompt_agent_response = prompt_agent.prompt_for_response(input_text)
    print(f"Agent Response: {prompt_agent_response.output_text}")
#end of function: test_web_search_tool

def test_code_tool(setup:FoundrySetup, model_deployment_name):
    # Give our prompt agent a unique name (this is how Foundry identifies it)
    agent_name = "code-tool-agent"
    model_deployment_name = "gpt-4.1" # Make sure we use a model which supports code generation
    # Create agent with code tool
    instructions_text = """You are a helpful assistant that can write and execute Python code to analyze data and create visualizations. 
        Always return the code you executed along with the results. 
        Analyze sales data and create visualizations."""
  
    # Upload a file to Foundry that the code agent can use (NOTE: you can reuse the same file for multiple agents/tools)
    uploaded_file_details = setup.upload_file("./inputs/coffee_shop_sales.csv")
   
    tool_definitions = {
            PromptAgentToolEnum.CODE: dict(
                uploaded_file_id=uploaded_file_details["id"])
                }

    request = FoundryPromptAgentRequest(
        agent_name = agent_name, 
        tool_definitions = tool_definitions,   
        model_deployment_name = model_deployment_name,
        instructions_text = instructions_text,
        input_text = "PENDING"
    )
    # Create the prompt agent with multiple tools using the tool definitions
    prompt_agent = FoundryPromptAgent(setup, request)

    # Check if the agent already exists in Foundry
    result = prompt_agent.agent_and_model_exist()
    # If exists with a different model, delete the existing agent
    if result == PromptAgentStatusEnum.FOUND_WITH_DIFFERENT_MODEL:
        prompt_agent.delete_agent(agent_name)
    
    # Now create with the correct deployment
    # Use the deployment name (we use the same as the model name) - the model MUST be deployed first
    if result == PromptAgentStatusEnum.NOT_FOUND or result == PromptAgentStatusEnum.FOUND_WITH_DIFFERENT_MODEL:
        prompt_agent.create_agent_version()

    # Send a message to the prompt agent and print the response
    request.input_text = """Calculate the total revenue (price * quantity) for each drink and create a horizontal bar chart 
        showing total revenue by drink, sorted from highest to lowest."""
    prompt_agent_response = prompt_agent.prompt_for_response(request)

    if prompt_agent_response and len(prompt_agent_response.outputs) > 0:
        file_output_info = prompt_agent_response.outputs[-1]
        output_file_id=file_output_info["output_file_id"] 
        output_container_id=file_output_info["output_container_id"]
        
        # Write the bytes to a local file
        output_filename=file_output_info["output_filename"]
        output_filepath = f"outputs/{output_filename}"
        raw_content = setup.download_file(output_file_id, output_container_id)
        with open(output_filepath, "wb") as local_file:
            local_file.write(raw_content.read())

        print(f"Chart saved and ready to view: {output_filepath}")
 
#end of function: test_code_tool



def test_multi_tool(setup:FoundrySetup, model_deployment_name): 
    agent_name = "multi-tool-agent"
    instructions_text="""You are a helpful assistant with two skills: 
            (1) you can suggest fun activities using the Bored Activity API, and 
            (2) you can search Microsoft Learn documentation. Use whichever tool is appropriate for the user's question, 
            or both if the question covers multiple topics."""
    input_text = """I'm bored: suggest a few DIY activities I can try, and also find me a Microsoft Learn tutorial about deploying Azure Container Apps."""
   
    # Create agent with mcp and openai tools
    tool_definitions = {
            PromptAgentToolEnum.MCP: dict(
                server_label="microsoft_learn_server", 
                server_url="https://learn.microsoft.com/api/mcp",
                require_approval="never"),
            PromptAgentToolEnum.OPENAI: dict(
            api_spec_file="./inputs/activities_openapi.json", 
            tool_name="activity-api-tool")
            }

    request = FoundryPromptAgentRequest(
        agent_name = "fitness-coach",  # Give our prompt agent a unique name (this is how Foundry identifies it)
        tool_definitions = tool_definitions,  # Pass the tool definitions to the agent request  
        model_deployment_name = model_deployment_name,
        instructions_text = instructions_text,
        input_text = input_text
    )
    # Create the prompt agent with multiple tools using the tool definitions
    prompt_agent = FoundryPromptAgent(setup, request)

    # Check if the agent already exists in Foundry
    result = prompt_agent.agent_and_model_exist()
    # If exists with a different model, delete the existing agent
    if result == PromptAgentStatusEnum.FOUND_WITH_DIFFERENT_MODEL:
        prompt_agent.delete_agent(agent_name)
    
    # Now create with the correct deployment
    # Use the deployment name (we use the same as the model name) - the model MUST be deployed first
    if result == PromptAgentStatusEnum.NOT_FOUND or result == PromptAgentStatusEnum.FOUND_WITH_DIFFERENT_MODEL:
        prompt_agent.create_agent_version()

    # Send a message to the prompt agent and print the response
    prompt_agent_response = prompt_agent.prompt_for_response(request)
    print(f"Agent Response: {prompt_agent_response['output_text']}")
#end of function

def test_memory_store(setup:FoundrySetup, model_deployment_name):

    # NOTE: OPTION 2: SAVING TO DIRECTLY TO STORE VIA APIs GAVE ERROR:
    # "Provided Azure resource encountered an error: Authentication failed.""

    # Give our prompt agent a unique name (this is how Foundry identifies it)
    agent_name = "memory-enabled-agent"
    memory_store_name = "personal-memory-store"
    embedding_model_name = "text-embedding-3-large"  # The embedding model MUST be deployed first
    user_scope_id = "user123"
    
    try:

        # Create the Memory Store FIRST
        memory_store = FoundryMemoryStore(setup, model_deployment_name, embedding_model_name, memory_store_name)
        print(f"\n✅ FoundryMemoryStore {memory_store_name} initialized successfully with the provided setup.")

        # Create the memory store in Foundry (if it doesn't already exist)
        if not memory_store.create_store():
            print(f"\n❌ Failed to create or access the memory store. Cannot proceed with memory tests.")
            return

        # OPTION 1: Use memories via an agent tool
        # https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/memory-usage?tabs=bash&pivots=python#use-memories-via-an-agent-tool
        
        # Create an agent with a memory store
        tools = [FoundryPromptAgentToolFactory.create_memory_tool(
                    memory_store_name="personal-memory-store",
                    scope=user_scope_id,
                    update_delay=1)]
        instructions_text="""You are a personalized assistant that remembers user preferences and past conversations to provide tailored responses. 
                When memory context is provided, use it to personalize your answers."""
        prompt_agent = FoundryPromptAgent(setup, agent_name=agent_name, model_deployment_name=model_deployment_name, 
                                tools=tools, instructions_text=instructions_text)
        # Check if the agent already exists in Foundry
        result = prompt_agent.agent_and_model_exist()
        # If exists with a different model, delete the existing agent
        if result == PromptAgentStatusEnum.FOUND_WITH_DIFFERENT_MODEL:
            prompt_agent.delete_agent(agent_name)
        
        # Now create with the correct deployment
        # Use the deployment name (we use the same as the model name) - the model MUST be deployed first
        if result == PromptAgentStatusEnum.NOT_FOUND or result == PromptAgentStatusEnum.FOUND_WITH_DIFFERENT_MODEL:
            prompt_agent.create_agent_version()

        input_text = """I prefer dark roast coffee."""
        prompt_agent_response = prompt_agent.prompt_for_response(input_text)
        print(f"Agent Response: {prompt_agent_response.output_text}")
        

        input_text = """Please order my usual coffee."""
        prompt_agent_response = prompt_agent.prompt_for_response(input_text)
        print(f"Agent Response: {prompt_agent_response.output_text}")


        # OPTION 2: Interact with the memory store directly via API calls from our code (without going through an agent tool)
        # https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/memory-usage?tabs=bash&pivots=python#use-memories-via-apis
        # Save a piece of information to the memory store for a specific user
        text_to_remember = "I prefer dark roast coffee and usually drink it in the morning"
        memory_store.save_to_memory(user_scope_id, text_to_remember)

        # Retrieve memories related to that user and print them out
        text_to_retrieve = "What are my coffee preferences?"
         
        text_to_remember = "I also like cappuccinos in the afternoon"
        memory_store.save_to_memory(user_scope_id, text_to_remember)

        retrieved_memories = memory_store.retrieve_from_memory(user_scope_id, text_to_retrieve)
        if retrieved_memories is not None:
            print(f"Found {len(retrieved_memories.memories)} memories")
            for memory in retrieved_memories.memories:
                print(f"  - Memory ID: {memory.memory_item.memory_id}, Content: {memory.memory_item.content}")

        #Delete the memories we created for cleanup (optional)
        memory_store.delete_scope(user_scope_id)

        memory_store.delete_store()

    except Exception as e:
        print(f"\n❌ Error during Memory Store testing: {e}")
        import traceback
        traceback.print_exc()

def test_image_service(setup:FoundrySetup):
    try:
        # Create and initialize the FoundryImageService object
        image_svc = FoundryImageService(setup)

        input_text = (
            "A vintage travel poster for a magical floating city above the clouds, "
            "with hot air balloons, golden sunlight, and the text "
            "'Visit Sky Harbor' at the bottom in bold retro lettering."
        )
        filename="outputs/sky_harbor_poster-openai.png"
        openai_response = image_svc.generate_image_openai(input_text=input_text, filename=filename)
        if openai_response is not None:
            print(f"✅ Image generated and saved successfully as {filename}.")

        filename="outputs/sky_harbor_poster-sdk.png"
        dict_json_response = image_svc.generate_image_sdk(input_text=input_text, filename=filename)
        if dict_json_response is not None:
            print(f"✅ Image generated and saved successfully as {filename}.")

    except Exception as e:
        print(f"\n❌ Error during test_image_service: {e}")
        traceback.print_exc()
    #end of function: test_image_service

def test_speech_service(setup:FoundrySetup):
    try:
        # Create and initialize the FoundrySpeech object
        voice_name = "en-us-Jenny:DragonHDLatestNeural"  # You can change this to any available voice
        speech_svc = FoundrySpeechService(setup, voice_name=voice_name)

        prompt = (
            "Cloud computing has revolutionized how businesses operate. "
            "Instead of maintaining expensive on-premises servers, companies "
            "can now rent computing power on demand from providers like "
            "Microsoft Azure, scaling up or down as their needs change."
        )
        filename="outputs/tts_output.wav"
        response = speech_svc.text_to_speech(prompt, filename)
        if response is not None:
            print(f"✅ Text-to-speech conversion completed successfully. Audio saved as {filename}.")
        else:
            print(f"\n❌ Text-to-speech conversion failed. No audio file was generated.")


        output_filename = "outputs/stt_output.txt"
        response = speech_svc.speech_to_text(input_audio_filename=filename, output_filename=output_filename)
        if response is not None:
            print(f"✅ Speech-to-text conversion completed successfully. Transcription saved as {output_filename}.")
        else:            
            print(f"\n❌ Speech-to-text conversion failed. No transcription file was generated.")

    except Exception as e:
        print(f"\n❌ Error during test_speech_service: {e}")
        traceback.print_exc()
    #end of function: test_speech_service

def test_language_service(setup:FoundrySetup):
    try:
        language_svc = FoundryLanguageService(setup)
        multilingual_samples = [
            "Bonjour, comment allez-vous aujourd'hui ?",
            "Ich lerne gerne neue Programmiersprachen.",
            "La inteligencia artificial está cambiando el mundo.",
        ]
        response = language_svc.detect_language(multilingual_samples)
        if response is not None:
            print(f"✅ Language detection completed successfully.")
        else:
            print(f"\n❌ Language detection failed.")

        tech_paragraph = [
            "Microsoft Azure provides a wide range of cloud services including "
            "virtual machines, Kubernetes clusters, serverless functions, and "
            "managed databases that help organizations scale their infrastructure."
        ]
        response = language_svc.extract_key_phrases(tech_paragraph)
        if response is not None:
            print(f"✅ Key phrase extraction for technical text completed successfully.")
        else:
            print(f"\n❌ Key phrase extraction for technical text failed.")

        review_samples = [
            "The new update is fantastic -- performance improved dramatically and the UI feels much smoother.",
            "I've been waiting three weeks for a response from support and still haven't heard back.",
            "The package arrived on Tuesday as scheduled.",
        ]
        response = language_svc.analyze_sentiment(review_samples)
        if response is not None:
            print(f"✅ Sentiment analysis for review samples completed successfully.")
        else:
            print(f"\n❌ Sentiment analysis for review samples failed.")


        news_snippets = [
            "In January 2025, OpenAI announced a partnership with Microsoft "
            "to invest $10 billion in artificial intelligence research at "
            "their campus in San Francisco."
        ]
        response = language_svc.recognize_entities(news_snippets)
        if response is not None:
            print(f"✅ Named entity recognition for news snippets completed successfully.")
        else:
            print(f"\n❌ Named entity recognition for news snippets failed.")

    except Exception as e:
        print(f"\n❌ Error during test_language_service: {e}")
        traceback.print_exc()
    #end of function: test_language_service

def test_search_service(setup:FoundrySetup, model_deployment_name: str):
    try:
        index_name = "idx-articles2"
        # NOTE! gpt-4.1 is OK, but the model CANNOT be -mini or -nano for RAG, otherwise you will get a max_tokens or max_completion_tokens error, 
        # because the smaller models have a much smaller token limit and RAG responses can easily exceed that limit.
        search_svc = FoundrySearchService(setup, index_name=index_name, 
                                          model_deployment_name=model_deployment_name)
        
        # Field Names, with id, this is added in the Search class
        field_names = ["title", "content", "category"]

        response = search_svc.create_index(index_name, field_names)

        if response is not None:
            print(f"✅ Create index completed successfully.")
        else:
            print(f"\n❌ Create index failed.")
        
         
        # Load documents from file
        with open("./inputs/search_articles.json", "r") as f:
            documents = json.load(f)
        response = search_svc.upload_documents(documents)

        if response is not None:
            print(f"✅ Upload documents completed successfully.")
        else:
            print(f"\n❌ Upload documents failed.")

        # Run a search query
        search_text = "machine learning applications"
        response = search_svc.search(search_text, top=5)
        if response is not None:
            print(f"✅ Search completed successfully.")
        else:
            print(f"\n❌ Search failed.")

        # Run a filtered search query
        search_text = "cloud computing"
        filter_expression = "category eq 'Technology'" # OData filter expression, set to "" for no filter
        response = search_svc.search(search_text, filter=filter_expression, top=5)
        if response is not None:
            print(f"✅ Filtered Search completed successfully.")
        else:
            print(f"\n❌ Filtered Search failed.")

        # RAG: Ask a question -- the model will search the index for relevant documents and use them to formulate its answer
        user_question = "What are the key benefits of cloud computing?"
        rag_response = search_svc.rag_search(user_question)
        if rag_response is not None:
            print(f"✅ RAG Search completed successfully.")
        else:
            print(f"\n❌ RAG Search failed.")

    except Exception as e:
        print(f"\n❌ Error during test_search_service: {e}")
        traceback.print_exc()
    #end of function: test_search_service


def test_translator_service(setup:FoundrySetup):
    try:
        # Source text in English
        original_text = "Artificial intelligence is transforming every industry around the world."
        to_languages= ["es", "de", "ja", "pt"]
        
        translator_svc = FoundryTranslatorService(setup)
        response = translator_svc.translate(original_text, to_languages=to_languages)
        if response is not None:
            print(f"✅ Language detection completed successfully.")
        else:
            print(f"\n❌ Language detection failed.")

    

    except Exception as e:
        print(f"\n❌ Error during test_language_service: {e}")
        traceback.print_exc()
    #end of function: test_language_service

if __name__ == "__main__":
    main()

