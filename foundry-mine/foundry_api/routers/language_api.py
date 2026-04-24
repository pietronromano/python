# This file defines the API endpoints for the agent-related operations in the FastAPI application. 
# It uses the FoundrySetupParams dependency to initialize the FoundrySetup and FoundryPromptAgent instances,
from fastapi import APIRouter, HTTPException, status


from foundry_api.dependencies import FoundrySetupDependency 
from foundry.language import FoundryLanguageService, FoundryLanguageRequest

# Don't forget to add this router to the main FastAPI app in main.py using app.include_router(agent.router)
# Create the FastAPI application instance
router = APIRouter(
    prefix="/language",
    tags=["language"],
)


@router.post("/detect")
async def detect_language(request: FoundryLanguageRequest, setup: FoundrySetupDependency):
    try:
        language_service = FoundryLanguageService(setup)
        response = language_service.detect_language(request)
        if response is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail="Failed to detect language")
        return response

    except Exception as e:
        setup.logger.error(f"An error occurred while processing the request ", exc=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="An server error occurred")
    
@router.post("/extract-key-phrases")
async def extract_key_phrases(request: FoundryLanguageRequest, setup: FoundrySetupDependency):
    try:
        language_service = FoundryLanguageService(setup)
        response = language_service.extract_key_phrases(request)
        if response is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail="Failed to extract key phrases")
        return response

    except Exception as e:
        setup.logger.error(f"An error occurred while processing the request ", exc=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="An server error occurred")
    
@router.post("/analyze-sentiment")
async def analyze_sentiment(request: FoundryLanguageRequest, setup: FoundrySetupDependency):
    try:
        language_service = FoundryLanguageService(setup)
        response = language_service.analyze_sentiment(request)
        if response is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail="Failed to analyze sentiment")
        return response

    except Exception as e:
        setup.logger.error(f"An error occurred while processing the request ", exc=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="An server error occurred")
    
@router.post("/recognize-entities")
async def recognize_entities(request: FoundryLanguageRequest, setup: FoundrySetupDependency):
    try:
        language_service = FoundryLanguageService(setup)
        response = language_service.recognize_entities(request)
        if response is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail="Failed to recognize entities")
        return response

    except Exception as e:
        setup.logger.error(f"An error occurred while processing the request ", exc=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="An server error occurred")