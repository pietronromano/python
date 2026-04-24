import sys
import subprocess
import json
import os
import traceback


from openai import OpenAI

# DefaultAzureCredential handles Azure login automatically
# It tries multiple login methods (VS Code, Azure CLI, etc.) until one works
from azure.identity import DefaultAzureCredential

# CognitiveServicesManagementClient lets us manage deployments on our Azure AI resource
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient

# AIProjectClient is the Foundry SDK client — we use it to list and test deployments
from azure.ai.projects import AIProjectClient

# For type hinting the conversation object: 
# The conversation object doesn't have a publicly exported type in the current SDK
from typing import Any 


from utils.logger import UtilsLogger
from utils.environment import UtilsEnvironment
from foundry.shared_models import FoundryChatResponse


class FoundrySetup:
    """Azure Foundry setup and configuration manager"""
    
    def __init__(self):
        """Initialize the FoundrySetup class with default values"""
        self.logger = None
        self.python_version = None
        self.python_path = None
        self.env_settings = {}
        self.required_packages = []
        self.available_models = []
        self.mgmt_client = None
        self.project_client = None

        self.found_project_api_key = None
        self.foundry_resource_name = None
        self.foundry_openai_endpoint = None
        self.foundry_cognitive_endpoint = None

        # Azure credential object (shared by both clients, also used for direct API calls if needed)
        self.credential = None
    
    def load_environment_config(self, env_file_path: str = "config/.env", logger_name="foundry_logger", logger_config_path: str = "config/logger.yml") -> bool: 
        """Load environment variables from .env file and store in self.env_settings dictionary.
            Also initializes the logger so we can log the results of all functions moving forward.
        Args:
            env_file_path: The path to the .env file (default is "config/.env": config folder in the root of the project)
            logger_name: The name of the logger to use (default is "foundry_logger")
            logger_config_path: The path to the logger configuration file (default is "config/logger.yml")
        Returns:
            True if loading was successful, False otherwise
        """
        try:
            self.env_settings = UtilsEnvironment.load_env_vars(env_file_path)
            if self.env_settings is None:
                print(f"❌ Failed to load environment variables.")
                return False
            # Setup logger
            self.logger = UtilsLogger(name=logger_name, logger_config_path=logger_config_path)
            self.logger.info("Environment variables loaded successfully.")
            return True
        except Exception as e:
            print(f"Error loading environment variables: {e}")
            self.env_settings = {}
            return False      
    # end of function

    def check_required_packages(self, requirements_path: str = "config/requirements.txt") -> bool:
        try:
            return UtilsEnvironment.check_required_packages(requirements_path)
        except Exception as e:
            self.logger.error(f"Error checking required packages: {e}")
            return False
    # end of function

    def check_python_version(self, desired_major: int = 3, desired_minor: int = 12) -> bool:
        """Check Python version"""

        # Delegate the actual version checking to the UtilsEnvironment class, but log the results here
        correct_version = UtilsEnvironment.check_python_version(desired_major, desired_minor)
        if correct_version:
            self.logger.info("Python version looks good.")
            return True
        else:
            self.logger.critical("Python version is not correct. Please install Python 3.12 and set it as the interpreter in VS Code.")
            return False
    # end of function

    def check_azure_cli_login(self):
        """Check Azure CLI login status"""
        self.logger.info("Checking Azure CLI Login Status")
        result = subprocess.run(["az", "account", "show"], capture_output=True, text=True)
        if result.returncode == 0:
            acct = json.loads(result.stdout)
            self.logger.info(f"Signed in as {acct['user']['name']}")
            self.logger.info(f"   Subscription: {acct['name']}")
            return True
        else:
            self.logger.error("Not signed in. Run 'az login' in your terminal first.")
            return False
    # end of function

    def login_azure_clients(self):
        """Initialize Azure clients using DefaultAzureCredential. 
        Also set calculated Endpoints based on environment variables."""
        self.logger.info("Initializing Azure Clients")
        
        try:
            
            # Create the credential object (shared by both clients, also used for direct API calls if needed)
            self.credential = DefaultAzureCredential()

            # Request a bearer token scoped to Azure Cognitive Services
            # This is the scope required for calling Foundry model endpoints
            self.token = self.credential.get_token("https://cognitiveservices.azure.com/.default").token
            self.logger.info(f"Credential Bearer token acquired: {self.token[:5]}...")

            self.foundry_project_api_key = self.env_settings["FOUNDRY_PROJECT_API_KEY"]
            self.foundry_resource_name = self.env_settings["FOUNDRY_RESOURCE_NAME"]
            # Endpoint for the Azure AI Services (AKA Cognitive Services): e.g. FLUX
            self.foundry_cognitive_endpoint = f"https://{self.foundry_resource_name}.cognitiveservices.azure.com"

            # Used for OpenAI SDK client configuration  (seems we need 2...)
            # Used for Image:
            self.foundry_openai_endpoint = f"https://{self.foundry_resource_name}.openai.azure.com/openai/v1"
            # Used for Search SDK configuration:
            self.azure_openai_endpoint = f"https://{self.foundry_resource_name}.openai.azure.com"

            # --- Client 1: Management client (for deploying models) ---
            # This client talks to the Azure Resource Manager (management plane)
            self.mgmt_client = CognitiveServicesManagementClient(
                credential=self.credential,
                subscription_id=self.env_settings["AZURE_SUBSCRIPTION_ID"],
            )
            self.logger.info("Management client connected!")

            # --- Client 2: AIProjectClient (for listing deployments and testing) ---
            # This client talks to the Foundry project (data plane)
            self.project_client = AIProjectClient(
                endpoint=self.env_settings["FOUNDRY_PROJECT_ENDPOINT"],
                credential=self.credential,
            )
            self.logger.info("AIProjectClient connected!")
            return True
        except Exception as e:
            self.logger.critical(f"Error during login_azure_clients: {e}")
            traceback.print_exc()
            return False
    # end of function

    def create_client_conversation(self, chat_conversation_id=None) -> tuple[OpenAI, Any]:
        # Get an OpenAI-compatible chat client from our Foundry connection
        # This client knows how to send messages and receive replies
        chat_client = self.project_client.get_openai_client()

        # Continue conversation if we have a conversation ID 
        if chat_conversation_id is not None:
            self.logger.info(f"Using existing conversation with ID: {chat_conversation_id}")
            chat_conversation = chat_client.conversations.retrieve(chat_conversation_id)
        else:
            chat_conversation = chat_client.conversations.create()
            # Show the conversation ID so we know it was created
            self.logger.info(f"Created Client and Conversation with id: {chat_conversation.id}")
        
        return chat_client, chat_conversation
    # end of function

    def process_client_response(self, client_response) -> FoundryChatResponse:
        """Convert the chat response object to a dictionary for easier access and testing
        
        Args:
            chat_response: The response object from the chat client
            
        Returns:
            A dictionary representation of the chat response
            Includes an empty 'outputs' list which can be populated with tool call results if needed

        """
        try:
            chat_response = FoundryChatResponse(
                response_id=client_response.id,
                output_text=client_response.output_text,
                instructions=client_response.instructions,
                model=client_response.model,
                total_tokens=client_response.usage.total_tokens,
                input_tokens=client_response.usage.input_tokens,
                output_tokens=client_response.usage.output_tokens,
                outputs=[]
            )
            return chat_response
        except Exception as e:
            self.logger.error(f"Error converting chat response to dict", exc=e)
            return None

    def chat_response_to_log_string(self, chat_response: FoundryChatResponse) -> str:
        """Convert the chat response dictionary to a concise log string"""
        try:
            log_info = (f"Chat Conversation Id: {chat_response.chat_conversation_id}| "
                        f"Response ID: {chat_response.response_id}| "
                        f"Output: {chat_response.output_text[:20]}...| "  # Log only the first 20 chars of the output for brevity
                        f"Model used: {chat_response.model}| "
                        f"Total tokens: {chat_response.total_tokens}| "
                        f"Input tokens: {chat_response.input_tokens}| "
                        f"Output tokens: {chat_response.output_tokens}|")
            return log_info
        except Exception as e:
            self.logger.error(f"Error converting dict response to log string", exc=e)
            return "Error formatting log info"

    def prompt_for_response(self, deployment_name, instructions_text, input_text):
        """Prompt directly for response from a deployed model, without using an agent"""
        self.logger.info("Get agent response...")
        
        # Make sure we have a chat client and conversation — if not, create them
        chat_client, chat_conversation = self.create_client_conversation()

        # Send our question to the AI model and store whatever it says in 'ai_response'
        # - 'model' tells the service which deployed model to use
        # - 'instructions' sets the AI's behavior (like giving it a role to play)
        # - 'input' is the actual question we want the AI to answer
        response = chat_client.responses.create(
            model=deployment_name,
            instructions=instructions_text,
            input=input_text,
        )
        chat_response = self.chat_response_to_dict(response)
        chat_response.chat_conversation_id = "<Not part of Chat>" # chat_response_to_dict expects chat_conversation_id
        log_info = self.chat_response_to_log_string(chat_response)
        self.logger.info(f"Response received: {log_info}\n")

        return chat_response
    # end of function

    def get_available_models(self, max_models=30):
        """List all models available for deployment"""
        self.logger.info("Available Models for Deployment")
        
        # Check if management client is initialized
        if not self.mgmt_client:
            self.logger.error("Management client not initialized. Run azure_default_login() first.")
            return
        
        # Check for required environment variables
        required_vars = ["AZURE_RESOURCE_GROUP", "FOUNDRY_RESOURCE_NAME"]
        missing_vars = []
        
        for var in required_vars:
            if var not in self.env_settings or not self.env_settings[var]:
                missing_vars.append(var)
        
        if missing_vars:
            self.logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            self.logger.error(f"   Please add these to your .env file")
            return
        
        try:
            # List all models available for our Cognitive Services account
            # This returns models that can be deployed in the region where our account lives
            available_models = self.mgmt_client.accounts.list_models(
                resource_group_name=self.env_settings["AZURE_RESOURCE_GROUP"],
                account_name=self.env_settings["FOUNDRY_RESOURCE_NAME"],
            )

            # Collect and display the models, grouped by format
            # 'format' is usually 'OpenAI' for GPT models or other publisher names
            self.available_models = []
            model_count = 0
            for model in available_models:
                model_count += 1
                # Store model info
                model_info = {
                    'name': model.name,
                    'version': model.version,
                }
                if model.capabilities:
                    model_info['capabilities'] = list(model.capabilities.keys()) 
                else:
                    model_info['capabilities'] = []

                self.available_models.append(model_info)
             
                # Stop after max_models to keep the output manageable
                if model_count >= max_models:
                    self.logger.info(f" ... showing first {max_models} of many models.")
                    break
            self.logger.info(f"\nTip: Visit https://ai.azure.com/catalog to browse the full catalog with descriptions.")
            return self.available_models
            
        except Exception as e:
            self.logger.error("Error listing models",e)
            return None
    # end of function
    
    def get_existing_deployments(self):
        """Return all existing model deployments in the Foundry account
        
        Returns: 
            - A list of deployments with details like model name, version, status, SKU, etc.  
            - None if there was an error (e.g. clients not initialized, API call failed, etc.)
        """
        self.logger.info("Existing Model Deployments")
        
        # Check if clients are initialized
        if not self.mgmt_client:
            self.logger.critical("Management client not initialized. Run azure_default_login() first.")
            return None
        
        try:
            # List all existing deployments
            deployments = self.mgmt_client.deployments.list(
                resource_group_name=self.env_settings["AZURE_RESOURCE_GROUP"],
                account_name=self.env_settings["FOUNDRY_RESOURCE_NAME"],
            )
            
            deployment_list = []
            deployment_count = 0
            
            for deployment in deployments:
                deployment_count += 1
                deployment_info = {
                    'name': deployment.name,
                    'model_name': deployment.properties.model.name,
                    'model_version': deployment.properties.model.version,
                    'model_format': deployment.properties.model.format,
                    'status': deployment.properties.provisioning_state,
                    'sku': deployment.sku.name if deployment.sku else 'N/A',
                    'capacity': deployment.sku.capacity if deployment.sku else 'N/A'
                }
                deployment_list.append(deployment_info)
                
                # Display deployment info
                self.logger.info(f" {deployment_count}. Deployment: {deployment_info['name']}")
                self.logger.info(f"     Model:    {deployment_info['model_name']} v{deployment_info['model_version']}")
                self.logger.info(f"     Format:   {deployment_info['model_format']}")
                self.logger.info(f"     Status:   {deployment_info['status']}")
                self.logger.info(f"     SKU:      {deployment_info['sku']} (capacity: {deployment_info['capacity']})")
            
            if deployment_count == 0:
                self.logger.info(" No deployments found.")
            else:
                self.logger.info(f" Total: {deployment_count} deployment(s)")
            
            return deployment_list
            
        except Exception as e:
            self.logger.error(f"Error listing deployments: {e}")
            self.logger.error(f"   Check your AZURE_RESOURCE_GROUP and FOUNDRY_RESOURCE_NAME values")
            return None
    # end of function
    
    def check_deployment_exists(self, deployment_name):
        """Check if a specific deployment exists by name"""
        if not self.mgmt_client:
            self.logger.error("Management client not initialized. Run azure_default_login() first.")
            return False
        
        try:
            deployment = self.mgmt_client.deployments.get(
                resource_group_name=self.env_settings["AZURE_RESOURCE_GROUP"],
                account_name=self.env_settings["FOUNDRY_RESOURCE_NAME"],
                deployment_name=deployment_name,
            )
            
            self.logger.info(f"Deployment '{deployment_name}' exists:")
            self.logger.info(f"   Model:  {deployment.properties.model.name} v{deployment.properties.model.version}")
            self.logger.info(f"   Status: {deployment.properties.provisioning_state}")
            self.logger.info(f"   SKU:    {deployment.sku.name} (capacity: {deployment.sku.capacity})")
            return True
            
        except Exception as e:
            if "NotFound" in str(e) or "ResourceNotFound" in str(e):
                self.logger.warning(f"Deployment '{deployment_name}' does not exist.")
                self.logger.warning("")
                return False
            else:
                self.logger.error(f"Error checking deployment: {e}")
                return False
    # end of function
    
    def get_model_details(self, model_name):
        # Verify the model exists and find its supported SKU
        # Different models support different SKUs (e.g., 'Standard', 'GlobalStandard', etc.)
        # We will automatically pick the first available SKU so the following deployment works correctly

        model_details = {"found": False}

        for model in self.mgmt_client.accounts.list_models(
            resource_group_name=self.env_settings["AZURE_RESOURCE_GROUP"],
            account_name=self.env_settings["FOUNDRY_RESOURCE_NAME"],
        ):
            if model.name == model_name:
                model_details["found"] = True
                model_details["name"] = model.name
                capabilities = ", ".join(model.capabilities.keys()) if model.capabilities else "N/A"
                model_details["capabilities"] = capabilities
                model_details["format"] = model.format
                model_details["version"] = model.version

                self.logger.info(f"Model found!")
                self.logger.info(f"  Name:         {model.name}")
                self.logger.info(f"  Version:      {model.version}")
                self.logger.info(f"  Format:       {model.format}")
                self.logger.info(f"  Capabilities: {capabilities}")

                # Show all available SKUs and pick the first one for deployment
                if model.skus:
                    sku_names = [s.name for s in model.skus]
                    self.logger.info(f"  Available SKUs: {', '.join(sku_names)}")

                    # Use the first SKU — this is typically the recommended one
                    first_sku = model.skus[0]
                    model_details["sku_name"] = first_sku.name
                    model_details["sku_capacity"] = first_sku.capacity.default if first_sku.capacity else 10

                    self.logger.info(f" Selected SKU for deployment:")
                    self.logger.info(f"    SKU:      {model_details['sku_name']}")
                    self.logger.info(f"    Capacity: {model_details['sku_capacity']}")

                    return model_details

        if not model_details["found"]:
            self.logger.warning(f"Model '{model_name}' was not found!")
            model_details["found"] = False
            return model_details
    # end of function

    def deploy_model(self, model_name, model_format=None, model_version=None, model_sku_name=None, model_sku_capacity=None):
        # Import the classes we need to define the deployment
        from azure.mgmt.cognitiveservices.models import (
            Deployment,              # The top-level deployment object
            DeploymentProperties,    # Configuration properties (model, version upgrade policy, etc.)
            DeploymentModel,         # Specifies which model to deploy
            Sku,                     # The pricing tier and capacity
        )

        # Check if model_format info was provided; if not, try to get it automatically based on the model info
        if not model_format:
            model_details = self.get_model_details(model_name)
            if not model_details["found"]:
                self.logger.error(f"Error: Model '{model_name}' not found. Cannot deploy.")
                return
        
        # Build the deployment definition
        # This is like filling out a form that tells Azure exactly what to create
        deployment = Deployment(
            properties=DeploymentProperties(
                model=DeploymentModel(
                    name=model_name,             # Which model (e.g., 'gpt-4.1-nano')
                    version=model_details["version"],       # Which version (e.g., '2025-04-14')
                    format=model_details["format"],         # Which format (e.g., 'OpenAI')
                ),
                # version_upgrade_option controls automatic updates:
                #   'NoAutoUpgrade' = stay on this exact version until we change it manually
                #   'OnceNewDefaultVersionAvailable' = auto-upgrade when a new default is released
                version_upgrade_option="NoAutoUpgrade",
            ),
            sku=Sku(
                name=model_details["sku_name"],         # SKU auto-detected in Step 5 (e.g., 'GlobalStandard')
                capacity=model_details["sku_capacity"],  # Default capacity from the model's SKU definition
            ),
        )

        self.logger.info(f"Deployment configuration:")
        self.logger.info(f"  Model:    {model_name}")
        self.logger.info(f"  Version:  {model_details['version']}")
        self.logger.info(f"  SKU:      {model_details['sku_name']}")
        self.logger.info(f"  Capacity: {model_details['sku_capacity']}")

        # Submit the deployment request and wait for it to finish
        # begin_create_or_update() starts the process; .result() waits until it is done
        self.logger.info(f"\nDeploying '{model_name}'...")
        self.logger.info("This usually takes about 1 minute. Please wait...\n")

        result = self.mgmt_client.deployments.begin_create_or_update(
            resource_group_name=self.env_settings["AZURE_RESOURCE_GROUP"],
            account_name=self.env_settings["FOUNDRY_RESOURCE_NAME"],
            deployment_name=model_name,
            deployment=deployment,
        ).result()

        # Print the result
        self.logger.info(f"Deployment complete!")
        self.logger.info(f"  Name:   {result.name}")
        self.logger.info(f"  Model:  {result.properties.model.name} v{result.properties.model.version}")
        self.logger.info(f"  Status: {result.properties.provisioning_state}")
        self.logger.info(f"  SKU:    {result.sku.name} (capacity: {result.sku.capacity})")
    # end of function
    
    def upload_file(self, file_path):
        """
        Upload a file to the Foundry service
        purpose="assistants" tells the service this file will be used by an agent/assistant
        Accepts either a file path (str/Path) or a file-like object bytes (e.g. from FastAPI File)
        NOTE: API doesn't let us use an explicit expires_after parameter

        References:
            - https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/files/sample_files.py
        Returns:
            - A dictionary with details about the uploaded file (id, name, size, etc.)

        """

        try:
            import os
            if isinstance(file_path, (str, os.PathLike)):
                file_data = open(file_path, "rb")
            else:
                file_data = file_path  # already a file-like object

            # openai.OpenAI
            chat_client = self.project_client.get_openai_client()
            # GAVE ERROR: "ADDITIONAL PROPERTIES NOT ALLOWED": expires_after=30*24*60*60,  # 30 days in seconds
            uploaded_file = chat_client.files.create(
                purpose="assistants",
                file=file_data,
            )

        
            # Print the file ID so we know the upload was successful
            self.logger.info(f"File uploaded successfully. ID: {uploaded_file.id}")
            return {"id": uploaded_file.id, "bytes": uploaded_file.bytes,
                        "filename": uploaded_file.filename, "purpose": uploaded_file.purpose,
                        "status": uploaded_file.status, "created_at": uploaded_file.created_at,
                        "expires_at": uploaded_file.expires_at}
        
        except FileNotFoundError:
            self.logger.error(f"Error: File not found at '{file_path}'")
            return None
        except Exception as e:
            self.logger.error(f"Error uploading file: {e}")
            return None
    #end of function

    def download_file(self, file_id: str,container_id: str = None):
        """
         Download a file from the Foundry service using its file ID
         If the file is in a container, we MUST provide the container_id to access it -> otherwise we get a "file not found" error even if the file ID is correct, because the service looks for the file in the wrong place without the container context
         
         References:
            - https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/files/sample_files.py
     
         Returns the raw bytes of the file content, or None if there was an error
         
         """

        # Download a file from the Foundry service using its file ID
        try:
            
            # openai.OpenAI
            chat_client = self.project_client.get_openai_client()
            meta_data = None
            raw_content = None
            # Retrieve the raw file from the service; if container_id is provided, retrieve from the container; otherwise, retrieve directly
            if container_id is None:
                raw_content = chat_client.files.content(file_id)
                meta_data = chat_client.files.retrieve(file_id)            
                  
            else:
                # Retrieve the  file  from the container
                meta_data = chat_client.containers.files.retrieve(
                    file_id= file_id,
                    container_id= container_id
                )
                raw_content = chat_client.containers.files.content.retrieve(
                    file_id=file_id,
                    container_id=container_id
                )
            
            return raw_content  # This is a file-like object containing the bytes of the file
        
        except Exception as e:
            self.logger.error(f"Error downloading file: {e}")
    #end of function
