# This file defines the API endpoints for the image_svc-related operations in the FastAPI application. 
# It uses the FoundrySetupParams dependency to initialize the FoundrySetup and FoundryPromptAgent instances,
from fastapi import APIRouter, HTTPException, status

from foundry_api.dependencies import FoundrySetupDependency 
from foundry.image import FoundryImageService, FoundryImageRequest



# Don't forget to add this router to the main FastAPI app in main.py using app.include_router(image_svc.router)
# Create the FastAPI application instance
router = APIRouter(
    prefix="/image",
    tags=["image"],
)

@router.post("/generate/sdk")
async def generate_image_sdk(request: FoundryImageRequest, setup: FoundrySetupDependency):
    try:
        image_svc = FoundryImageService(setup)

        # Send a message to image_svc and print the response
        svc_response = image_svc.generate_image_sdk(request)    
        if svc_response is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail="Failed to get a response from the image_svc")
        # FastAPI automatically converts dict to JSON
        return svc_response

    except Exception as e:
        setup.logger.error(f"An error occurred while processing the request ", exc=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="An server error occurred")
    

@router.post("/generate/openai")
async def generate_image_openai(request: FoundryImageRequest, setup: FoundrySetupDependency):
    try:
        image_svc = FoundryImageService(setup)

        # Send a message to image_svc and print the response
        svc_response = image_svc.generate_image_openai(request)    
        if svc_response is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail="Failed to get a response from the image_svc")
        # OpenAI SDK returns a response object that is not JSON serializable, so image_svc just returns the base64 string of the image data instead, 
        # Which is JSON serializable. The actual image file is saved locally on the server.
        # FastAPI automatically converts dict to JSON
        return {"b64_image_data": svc_response}

    except Exception as e:
        setup.logger.error(f"An error occurred while processing the request ", exc=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="An server error occurred")