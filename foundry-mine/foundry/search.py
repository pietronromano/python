"""
 Utility class encapsulating the Azure Search Service 
 Pre-requisites: 
    - Azure Foundry resource with an OpenAI model deployed that supports RAG (e.g. "gpt-5.4-nano")
    - Azure AI Search service (for full-text search and filtering).
        - Search INDEX populated with documents after deployment: e.g. idx-articles: id, title, content, category
    - azure-search-documents-11.6.0

    - RBAC requirements: (Avoid: "Error during create_index: Operation returned an invalid status 'Forbidden'")
        - NOTE: "API Access control" must be set to RBAC or Both, NOT just "API Keys"
        - "Search Service Contributor" on the AI Search resource (to create indexes)
        - "Search Index Data Contributor" on the AI Search resource (to upload docs)
        - "Search Index Data Reader" on the AI Search resource (to query)

 References:
    - Overview: https://learn.microsoft.com/en-us/azure/search/search-what-is-azure-search?tabs=indexing%2Cquickstarts: 
    - Search SDK Documentation: https://learn.microsoft.com/en-us/python/api/overview/azure/search-documents-readme?view=azure-python
"""

import traceback

import time
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, SearchFieldDataType,
    SemanticConfiguration, SemanticSearch, SemanticField, SemanticPrioritizedFields,

)
from azure.search.documents import SearchClient 

from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


from .setup import FoundrySetup

class FoundrySearchService:
    
    def __init__(self, setup: FoundrySetup, index_name: str, model_deployment_name: str):
        """
        Initialize the Search Object with FoundrySetup.
        
        Args:
            setup: FoundrySetup object that is already initialized and logged in
            index_name: Name of the Azure Search index to use
            model_deployment_name: Name of the Azure OpenAI model deployment to use
            # NOTE! gpt-4.1 is OK, but the model CANNOT be -mini or -nano for RAG, otherwise you will get a max_tokens or max_completion_tokens error, 
            #  because the smaller models have a much smaller token limit and RAG responses can easily exceed that limit.
       
        """
        try:
            self.setup = setup
            self.index_name = index_name
            self.model_deployment_name = model_deployment_name
            # Azure AI Search settings
            self.search_endpoint = self.setup.env_settings["SEARCH_ENDPOINT"]
            print("Search Endpoint:", self.search_endpoint)


        except Exception as e:
            print(f"\n❌ Error during __init__: {e}")
            traceback.print_exc()
    #end of function: __init__

    def create_index(self, field_names: list[str]): 
        """
        Create a search index in Azure Search.
        
        Args:
            field_names: List of field names to include in the index
        """
        try:
            print(f"Creating index... Name: {self.index_name}")
            index_client = SearchIndexClient(endpoint=self.search_endpoint, 
                                             credential=self.setup.credential)
            fields = [
                SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True)]
            
            for field_name in field_names:
                fields.append(SearchableField(name=field_name, type=SearchFieldDataType.String, filterable=True, sortable=True))

            semantic_config = SemanticConfiguration(
                name="my-semantic-config",
                prioritized_fields=SemanticPrioritizedFields(
                    content_fields=[SemanticField(field_name="content")],
                    title_field=SemanticField(field_name="title"),
                ),
            )
            index = SearchIndex(
                name=self.index_name,
                fields=fields,
                semantic_search=SemanticSearch(configurations=[semantic_config]),
            )
            result = index_client.create_or_update_index(index)
            print(f"Index created: {result.name}")
            return result
            
        except Exception as e:
            print(f"\n❌ Error during create_index: {e}")
            traceback.print_exc()
            return None
    #end of function: create_index

    def upload_documents(self, documents: list[dict]):
        """
        Upload documents to the Azure Search index.
        
        Args:
            documents: List of documents to upload
        """
        try:
            print(f"Uploading {len(documents)} documents to index: {self.index_name}")
           
            search_client = SearchClient(endpoint=self.search_endpoint, index_name=self.index_name, credential=self.setup.credential)
            upload_result = search_client.upload_documents(documents=documents)
            succeeded = sum(1 for r in upload_result if r.succeeded)
            print(f"Uploaded {succeeded}/{len(documents)} documents")
            return upload_result
            
        except Exception as e:
            print(f"\n❌ Error during upload_documents: {e}")
            traceback.print_exc()
            return None
    #end of function: upload_documents

    def search(self, search_text: str, filter: str = "", top: int = 5):
        """
        Perform a search query on the Azure Search index.
        
        Args:
            search_text: The search query text
            filter: Optional OData filter expression to narrow down results (e.g. "category eq 'Technology'")
            top: Number of top results to return
        """
        try:
            print(f"Searching... search_text: {search_text}")
            search_client = SearchClient(
                endpoint=self.search_endpoint,
                index_name=self.index_name,
                credential=self.setup.credential,
            )
            print(f"Search client connected to index '{self.index_name}'")

            results = search_client.search(
                search_text=search_text,
                filter=filter,                   # Optional OData filter expression
                top=top,                       # Return the top K results
                include_total_count=True,    # Include the total number of matches
            )
            print(f"Total matches: {results.get_count()}\n")

            for i, result in enumerate(results, start=1):
                score = result.get("@search.score", "N/A")
                print(f"  {i}. [Score: {score}]")
                for key, value in result.items():
                    if not key.startswith("@"):
                        display_val = str(value)[:120]
                        print(f"     {key}: {display_val}")
                print()
            return results

        except Exception as e:
            print(f"\n❌ Error during search: {e}")
            traceback.print_exc()
            return None
    #end of function: search

    def rag_search(self, user_question: str, temperature: float = 0.7):
        """
        Perform a search query with Retrieval-Augmented Generation (RAG) capabilities on the Azure Search index.
        
        NOTE! gpt-4.1 is OK, but the model CANNOT be -mini or -nano for RAG, otherwise you will get a max_tokens or max_completion_tokens error, 
        #  because the smaller models have a much smaller token limit and RAG responses can easily exceed that limit.
       
        Args:
            user_question: The question to ask the model
            max_completion_tokens: Maximum tokens for the model's response (must be within the model's limits, e.g. 4096 for gpt-4.1)
            temperature: Sampling temperature for the response
        """
        try:
            # Create a token provider for the OpenAI client
            token_provider = get_bearer_token_provider(
                self.setup.credential,
                "https://cognitiveservices.azure.com/.default",
            )

            # Create the Azure OpenAI client using Entra ID
            openai_client = AzureOpenAI(
                api_version="2024-12-01-preview",
                azure_endpoint=self.setup.azure_openai_endpoint,
                azure_ad_token_provider=token_provider,
            )

            # For the data source, we also need a bearer token for the search service
            search_token = self.setup.credential.get_token("https://search.azure.com/.default").token

            # Configure the search index as a data source for RAG
            rag_config = {
                "data_sources": [
                    {
                        "type": "azure_search",
                        "parameters": {
                            "endpoint": self.search_endpoint,
                            "index_name": self.index_name,
                            "authentication": {
                                "type": "access_token",
                                "access_token": search_token,
                            },
                        },
                    }
                ],
            }

            # NOTE:max_completion_tokens not allowed: "#/max_completion_tokens: Extra inputs are not permitted'}}"
            rag_response = openai_client.chat.completions.create(
                messages=[
                    {"role": "user", "content": user_question},
                ],
                temperature=temperature,
                model=self.model_deployment_name,
                extra_body=rag_config,
            )

            print(f"Question: {user_question}\n")
            print(f"RAG Answer:\n{rag_response.choices[0].message.content}")
            return rag_response               
        except Exception as e:
            print(f"\n❌ Error during RAG search: {e}")
            traceback.print_exc()
            return None
    #end of function: rag_search


    