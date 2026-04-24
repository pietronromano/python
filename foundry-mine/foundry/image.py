"""
Utility class to provide image capabilities, using the OpenAI Images API
Pre-requisites: 
    - Flux.1-Kontext-pro model deployed in Azure Foundry (or another model that supports image generation: output type = image)
    - FoundrySetup object that is already initialized and logged in (login_azure_clients), to provide authentication and configuration for API calls

    
API Version Notes:
    - IMAGE_API_VERSION="preview": - >THIS GAVE A 404! Resource Not Found error
    so switched to the specific version "2025-04-01-preview" 
    - This worked fine: -> IMAGE_API_VERSION="2025-04-01-preview"


References:
- https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-flux?tabs=python
- https://github.com/microsoft-foundry/foundry-samples/blob/main/samples/python/black-forest-labs/flux/README.md
"""

# base64 lets us decode the image data returned by the API
import base64
import os
from urllib import response

# requests lets us make HTTP calls to the FLUX endpoint
from openai import OpenAI
import requests
from pydantic import BaseModel

from azure.identity import DefaultAzureCredential

from .setup import FoundrySetup


# Pydantic model for the Image request body 
class FoundryImageRequest(BaseModel):
    input_text: str # The prompt for the image generation
    filename: str = "outputs/image.png"
    n: int = 1
    size: str = "1024x1024"
    output_format: str = "png"


class FoundryImageService: 
    def __init__(self, setup: FoundrySetup):
        """
        Initialize the Image Object
        
        Args:
            setup: FoundrySetup object that is already initialized and logged in (login_azure_clients)
        """
        try:
            self.setup = setup
            self.logger = setup.logger
            self.image_model_deployment_name = self.setup.env_settings["IMAGE_MODEL_DEPLOYMENT_NAME"]
            self.image_api_version = self.setup.env_settings["IMAGE_API_VERSION"]
          
            if not self.image_model_deployment_name:
                raise ValueError("IMAGE_MODEL_DEPLOYMENT_NAME is not set in environment settings")
            if not self.image_api_version:
                raise ValueError("IMAGE_API_VERSION is not set in environment settings")

        except Exception as e:
            self.logger.error(f"Error during __init__:", exc=e)
    #end of function

    def generate_image_openai(self, image_request: FoundryImageRequest) -> str | None:
        """
        WORKED OK!
        Using the OpenAI SDK, generate an image based on a text prompt using the FLUX model.
        
        Args:
            image_request: FoundryImageRequest object containing the image generation parameters
        Returns:
            the base64 string of the image data (not the full response object, which is not JSON serializable), None otherwise. The generated image will be saved to a local file.
        """
        try:
            # Build the request body according to the API specification
            data = {
                "prompt": image_request.input_text,
                "n": image_request.n,
                "size": image_request.size,
                "output_format": image_request.output_format,
                "model": self.image_model_deployment_name,
            }

            # OpenAI REQUIRES an API key
            client = OpenAI(
                base_url=self.setup.foundry_openai_endpoint,
                api_key=self.setup.foundry_project_api_key
            )

            self.logger.info(f"Sending request to OpenAI image generation endpoint: {client.base_url}")
            response = client.images.generate(**data)
            # Using the OpenAI SDK client now, which returns an ImagesResponse object, not a dictionary. 
            # WE need to access its attributes using dot notation instead of subscript notation.
            b64_image_data = response.data[0].b64_json
            
            if (b64_image_data is None) or (len(b64_image_data) == 0):
                self.logger.error("No image data found in the response.")
                return None
            image_bytes = base64.b64decode(b64_image_data)
            # Save the image to a local file
            with open(image_request.filename, "wb") as f:
                f.write(image_bytes)
            self.logger.info(f"Image saved: {os.path.abspath(image_request.filename)}")
            return b64_image_data # Return the base64 string of the image data (not the full response object, which is not JSON serializable)
           
        except Exception as e:
            self.logger.error(f"Error during image generation:", exc=e)
            return None
    #end of function

    def generate_image_sdk(self, image_request: FoundryImageRequest) -> dict | None:
        """
        Using the Image SDK, generate an image based on a text prompt using the FLUX model.
        
        Args:
            image_request: FoundryImageRequest object containing the image generation parameters
        Returns:
            Dict containing API response if successful, None otherwise. The generated image will be saved to a local file.
        """
        try:
            # Build the request body according to the API specification
            data = {
                "prompt": image_request.input_text,
                "n": image_request.n,
                "size": image_request.size,
                "output_format": image_request.output_format,

            }

            headers = {
                "Authorization": f"Bearer {self.setup.token}",
                "Content-Type": "application/json",
            }
                
            generation_url = (
                f"{self.setup.foundry_cognitive_endpoint}/openai/deployments/{self.image_model_deployment_name}"
                f"/images/generations?api-version={self.image_api_version}"
            )

            # # Make the POST request to the FLUX image generation endpoint
            self.logger.info(f"Sending request to SDK FLUX image generation endpoint: {generation_url}")
            response = requests.post(generation_url, headers=headers, json=data)
            # Check if the request was successful
            if response.status_code != 200:
                self.logger.error(f"Image generation failed with status code {response.status_code}: {response.text}")
                return None
            # Check if the request succeeded
            response.raise_for_status()
            dict_json_response = response.json() # Converts to a dict.The response format is: {"data": [{"b64_json": "..."}]}
            self.logger.info("Image generated successfully!")
            
            # Extract the base64-encoded image from the response
            # The response format is: {"data": [{"b64_json": "..."}]}
            b64_image_data = dict_json_response["data"][0]["b64_json"]
            # Decode the base64 string into raw image bytes
            if (b64_image_data is None) or (len(b64_image_data) == 0):
                self.logger.error("No image data found in the response.")
                return None
            image_bytes = base64.b64decode(b64_image_data)
            # Save the image to a local file
            with open(image_request.filename, "wb") as f:
                f.write(image_bytes)
            self.logger.info(f"Image saved: {os.path.abspath(image_request.filename)}")
            return dict_json_response
           
        except Exception as e:
            self.logger.error(f"Error during image generation:", exc=e)
            return None
    #end of function
