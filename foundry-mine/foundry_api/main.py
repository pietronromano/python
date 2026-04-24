
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path


from foundry_api.routers import setup_api,image_api, language_api, prompt_agent_api


# Create the FastAPI a
app = FastAPI()

# Add routers to the main FastAPI app
app.include_router(prompt_agent_api.router)
app.include_router(image_api.router)
app.include_router(language_api.router)
app.include_router(setup_api.router)

# Serve static files from a directory (relative to this file's location)
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
# Serve favicon from static folder
@app.get('/favicon.ico')
async def favicon():
    favicon_path = static_dir / "favicon.ico"
    return FileResponse(favicon_path, media_type="image/x-icon")

@app.get("/")
async def root():
    return {"message": "Welcome to the Foundry API! Visit /docs for API documentation."}
