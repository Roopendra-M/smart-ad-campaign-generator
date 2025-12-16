from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

# 🔥 FORCE .env to override Windows env vars
load_dotenv(override=True)

# Import modules
from src import models
from src.campaign_routes import router as campaign_router
from src.routes import router as main_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database on startup."""
    await models.init_mongodb()
    yield


app = FastAPI(title="Ad Campaign Dashboard", lifespan=lifespan)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Routers
app.include_router(main_router)
app.include_router(campaign_router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
