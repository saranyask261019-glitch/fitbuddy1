from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from .database import Base, engine
from . import models  # ensure models are registered before create_all
from .routes import router

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="FitBuddy AI Fitness Plan Generator", version="1.0.0", lifespan=lifespan,
              description="Generate a 7-day fitness plan, receive general nutrition tips, and revise plans with feedback.")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(router)
