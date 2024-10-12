from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.routes import router as api_router
from app.core.config import settings
from app.services.agent_service import AgentService

app = FastAPI(title=settings.PROJECT_NAME)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Initialize AgentService
agent_service = AgentService()

# Include the router
app.include_router(api_router)

# Make agent_service available to the routes
app.state.agent_service = agent_service

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
