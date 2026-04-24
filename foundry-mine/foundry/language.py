"""
 Utility class encapsulating the Azure Foundry Tools Speech SDK (Previously Cognitive Services Speech SDK) 
 Pre-requisites: 
    - Azure Language Resource
    - azure.ai.textanalytics==5.4.0

 References:
    - Overview: https://learn.microsoft.com/en-gb/azure/ai-services/language-service/overview
    - Azure Text Analytics client library for Python - version 5.4.0: https://learn.microsoft.com/en-us/python/api/overview/azure/ai-textanalytics-readme?view=azure-python
 """


from azure.ai.textanalytics import TextAnalyticsClient

from .setup import FoundrySetup
from pydantic import BaseModel

# Pydantic model for the request body when calling our API
class FoundryLanguageRequest(BaseModel):
    documents: list  

class FoundryLanguageService:
    """Utility class to provide language capabilities to Azure Foundry Agents"""
    
    def __init__(self, setup: FoundrySetup):
        """
        Initialize the Language Object with FoundrySetup.
        
        Args:
            setup: FoundrySetup object that is already initialized and logged in
        """
        try:
            self.setup = setup
            self.logger = setup.logger
            self.language_endpoint = self.setup.env_settings["LANGUAGE_ENDPOINT"]
            self.logger.info(f"Endpoint: {self.language_endpoint}")
          
            self.ta_client = TextAnalyticsClient(
                endpoint=self.language_endpoint,
                credential=self.setup.credential,
            )

        except Exception as e:
            self.logger.error("Error during __init__", exc=e)
    #end of function

    def detect_language(self, request: FoundryLanguageRequest ) -> dict:
        """
        Detect the language of the input text.
        
        Args:
            request: A FoundryLanguageRequest object containing the documents to detect the language of
        Returns:
            The detected language code (e.g. "en", "fr", etc.) or None if detection failed
        """
        try:
            self.logger.info("FoundryLanguageService: Detect Language: Calling TextAnalyticsClient.detect_language()")
            response = self.ta_client.detect_language(documents=request.documents)
            if response:
                dict_json_response = {"results": []}
                for doc, result in zip(request.documents, response):
                    dict_result ={
                        "id": result.id,
                        "is_error": result.is_error,
                        "kind": result.kind,
                        "input_document": doc,
                        "language_name": result.primary_language.name,
                        "confidence_score": result.primary_language.confidence_score,
                        "iso6391_name" : result.primary_language.iso6391_name,
                    }
                    dict_json_response["results"].append(dict_result)
                    self.logger.info(f"Language detection Result: language_name:{dict_result['language_name']}, confidence_score:{dict_result['confidence_score']:.2f}")

                return dict_json_response
            else:
                return None
        except Exception as e:
            self.logger.error("Error during detect_language", exc=e)
            return None 
    #end of function: 

    def extract_key_phrases(self, request: FoundryLanguageRequest ) -> dict:
        """
        Extract key phrases from the input text.
        
        Args:
            request: A FoundryLanguageRequest object containing the documents to extract key phrases from
        Returns:
            A list of key phrases or None if extraction failed
        """
        try:
            self.logger.info("FoundryLanguageService: Extract Key Phrases: Calling TextAnalyticsClient.extract_key_phrases()")
            response = self.ta_client.extract_key_phrases(documents=request.documents)
            if response:
                dict_json_response = {"results": []}
                for doc, result in zip(request.documents, response):
                    dict_result = {
                        "id": result.id,
                        "input_document" : doc,
                        "is_error": result.is_error,
                        "kind": result.kind,
                        "key_phrases": []
                    }
                    for phrase in result.key_phrases:
                        dict_result["key_phrases"].append(phrase)
                    dict_json_response["results"].append(dict_result)
                    self.logger.info(f"Extract Key Phrases Result: # Key Phrases:{len(dict_result['key_phrases'])}")
                return dict_json_response
            else:
                return None
        except Exception as e:
            self.logger.error("Error during extract_key_phrases", exc=e)
            return None 
    #end of function


    def analyze_sentiment(self, request: FoundryLanguageRequest ) -> dict:
        """
        Analyze the sentiment of the input text.
        
        Args:
            request: A FoundryLanguageRequest object containing the documents to analyze sentiment from
        Returns:
            A list of sentiment scores or None if analysis failed
        """
        try:
            self.logger.info("FoundryLanguageService: Analyze Sentiment: Calling TextAnalyticsClient.analyze_sentiment()")
            response = self.ta_client.analyze_sentiment(documents=request.documents)
            if response:
                dict_json_response = {"results": []}
                for result in response:
                        sentence = result.sentences[0]
                        dict_result = {
                            "id": result.id,
                            "is_error": result.is_error,
                            "kind": result.kind,
                            "sentiment": result.sentiment,
                            "sententce_text": sentence.text,
                            "confidence_scores_positive":sentence.confidence_scores.positive,
                            "confidence_scores_neutral":sentence.confidence_scores.neutral,
                            "confidence_scores_negative":sentence.confidence_scores.negative,  
                        }
                        dict_json_response["results"].append(dict_result)
                        self.logger.info(f"Analyze Sentiment Result: Id:{dict_result['id']}, # Sentimient:{dict_result['sentiment']}")

                return dict_json_response
            else:
                return None
        except Exception as e:
            self.logger.error("Error during analyze_sentiment", exc=e)
            return None 
    #end of function


    def recognize_entities(self, request: FoundryLanguageRequest ) -> dict:
        """
        Recognize entities in the input text.
        
        Args:
            request: A FoundryLanguageRequest object containing the documents to recognize entities from
        Returns:
            A list of entities or None if recognition failed
        """
        try:
            self.logger.info("FoundryLanguageService: Recognize Entities: Calling TextAnalyticsClient.recognize_entities()")
            response = self.ta_client.recognize_entities(documents=request.documents)
            if response:
                dict_json_response = {"results": []}
                for result in response:
                    dict_result = {
                        "id": result.id,
                        "is_error": result.is_error,
                        "kind": result.kind,
                        "entities": []
                        }
                    for entity in result.entities:
                        dict_result["entities"].append({
                            "text": entity.text,
                            "length": entity.length,
                            "offset": entity.offset,
                            "category": entity.category,
                            "subcategory": entity.subcategory,
                            "confidence_score": entity.confidence_score,
                        })
                    dict_json_response["results"].append(dict_result)
                    self.logger.info(f"Recognize Entities Result: Id:{dict_result['id']}, # Entities:{', '.join([entity['text'] for entity in dict_result['entities']])}")
                return dict_json_response
            else:
                return None
        except Exception as e:
            self.logger.error("Error during recognize_entities", exc=e)
            return None 
    #end of function