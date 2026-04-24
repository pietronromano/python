"""
 Utility class encapsulating the Azure Foundry Tools Translator SDK (Previously Cognitive Services Translator SDK) 
 Pre-requisites: 
    - Azure Translation Resource
    - NOT NEEDED? azure-ai-translation-text==1.0.1

 References:
    - Udemy: https://www.udemy.com/course/microsoft-foundry/learn/lecture/54848481#overview
    - Overview: https://learn.microsoft.com/en-gb/azure/ai-services/translator/
    - Azure Text Translation client library for Python - version 1.0.1: https://learn.microsoft.com/en-us/python/api/overview/azure/ai-translation-text-readme?view=azure-python&preserve-view=true
 """

import traceback

from azure.identity import DefaultAzureCredential
import requests

from .setup import FoundrySetup

class FoundryTranslatorService:

    def __init__(self, setup: FoundrySetup):
        """
        Initialize the Language Object with FoundrySetup.
        
        Args:
            setup: FoundrySetup object that is already initialized and logged in
        """
        try:
            self.setup = setup

            self.language_endpoint = self.setup.env_settings["LANGUAGE_ENDPOINT"]
            self.region = self.setup.env_settings["TRANSLATOR_REGION"]
            self.document_endpoint = self.setup.env_settings["TRANSLATOR_DOCUMENT_ENDPOINT"]
            # Build the request URL
            self.document_translate_url = f"{self.document_endpoint}translator/text/v3.0/translate"
            print("Document Endpoint:", self.document_endpoint)

            # Common headers for every Translator REST call
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "Ocp-Apim-Subscription-Region": self.region,
            }

        except Exception as e:
            print(f"\n❌ Error during __init__: {e}")
            traceback.print_exc()
    #end of function: __init__

    def translate(self, original_text: str, from_language: str = None, to_languages: list = None) -> str:
        """
        Translate the input text.
        
        Args:
            documents: A list of documents to translate. Each document should be a dictionary with the following structure:
        Returns:
            The detected language code (e.g. "en", "fr", etc.) or None if detection failed
        """
        try:
            
            params = {
                "to": to_languages,
                "api-version": "3.0"
            }
            # if from_language is not None
            if from_language is not None:
                params["from"] = from_language

            response = requests.post(
                self.document_translate_url,
                headers=self.headers,
                params=params,
                json=[{"Text": original_text}],
            )
            response.raise_for_status()
            result = response.json()

            translated = result[0]["translations"][0]["text"]
            print(f"Original (en):    {original_text}")
            print(f"Translated (fr):  {translated}")
            if response:
                for translation in result[0]["translations"]:
                    print(f"  [{translation['to']}]  {translation['text']}")
                    return response
            else:
                return None
        except Exception as e:
            print(f"\n❌ Error during translate: {e}")
            traceback.print_exc()
            return None 
    #end of function: translate

   