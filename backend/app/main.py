from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from .api.v1 import audio

# Load environment variables
load_dotenv()

app = FastAPI(
    title=os.getenv("PROJECT_NAME", "Audio Research API"),
    openapi_url=f"{os.getenv('API_V1_PREFIX', '/api/v1')}/openapi.json"
)

# Configure CORS
origins = eval(os.getenv("BACKEND_CORS_ORIGINS", '["http://localhost:5173"]'))
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    audio.router,
    prefix=os.getenv("API_V1_PREFIX", "/api/v1"),
    tags=["audio"]
)

@app.get("/")
async def root():
    return {"message": "Welcome to Audio Research API"}

# Import and include routers here
# from app.api.v1 import some_router
# app.include_router(some_router.router, prefix=os.getenv("API_V1_PREFIX", "/api/v1")) 