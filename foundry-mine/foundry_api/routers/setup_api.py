# FoundrySetup API Router
# Prerequisite: for handling file uploads: $ pip install python-multipart

import mimetypes
from typing_extensions import Annotated

from fastapi import (
    APIRouter, Depends, HTTPException, status, File, UploadFile
)
from fastapi.responses import Response

from foundry_api.dependencies import FoundrySetupDependency 

# Don't forget to add this router to the main FastAPI app in main.py using app.include_router(agent.router)
# Create the FastAPI application instance
router = APIRouter(
    prefix="/setup",
    tags=["setup"],
)

    
# Reference: https://fastapi.tiangolo.com/tutorial/request-files/
# A simple File param is enough to get the file contents as bytes
@router.post("/upload_file")
async def upload_file(setup: FoundrySetupDependency, file: Annotated[bytes, File()]):
    try:
        uploaded_file = setup.upload_file(file)
        if uploaded_file is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail="Failed to upload file")
        return uploaded_file

    except Exception as e:
        setup.logger.error(f"An error occurred while processing the request ", exc=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="An server error occurred")
    
@router.get("/download_file")
async def download_file(setup: FoundrySetupDependency, file_id: str, container_id: str = None, filename: str = "download"):
    try:
        file_content = setup.download_file(file_id, container_id)
        if file_content is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail="File not found")
        raw_bytes = file_content.read()

        # Detect media type from filename extension, default to octet-stream for unknown binary
        media_type, _ = mimetypes.guess_type(filename)
        if media_type is None:
            media_type = "application/octet-stream"

        return Response(
            content=raw_bytes,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        setup.logger.error(f"An error occurred while processing the request ", exc=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="An server error occurred")
    