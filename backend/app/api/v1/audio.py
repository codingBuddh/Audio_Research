from fastapi import APIRouter, UploadFile, WebSocket, HTTPException, Form, File
from ...services.audio.task_manager import AudioTaskManager
from ...schemas.audio import AudioAnalysisRequest, AudioAnalysisResponse, AudioFeatureType
import os
import json
from tempfile import NamedTemporaryFile
import shutil

router = APIRouter()
task_manager = AudioTaskManager()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/analyze", response_model=AudioAnalysisResponse)
async def analyze_audio(
    file: UploadFile = File(...),
    feature_types: str = Form(...),
    chunk_duration: float = Form(60.0)
):
    """
    Upload and analyze an audio file.
    The analysis will be performed in chunks of 1 minute each, and results will be streamed via WebSocket.
    """
    try:
        # Parse feature types from JSON string
        feature_types_list = [AudioFeatureType(ft) for ft in json.loads(feature_types)]
        
        # Save the uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create analysis task
        task_id = await task_manager.create_task(
            file_path=file_path,
            feature_types=feature_types_list,
            chunk_duration=chunk_duration
        )
        
        return task_manager.get_task_status(task_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Invalid feature type: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{task_id}", response_model=AudioAnalysisResponse)
async def get_analysis_status(task_id: str):
    """Get the current status of an audio analysis task"""
    task = task_manager.get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """WebSocket endpoint for receiving real-time updates about the analysis"""
    await websocket.accept()
    
    task = task_manager.get_task_status(task_id)
    if not task:
        await websocket.close(code=4004, reason="Task not found")
        return
    
    try:
        # Register the WebSocket connection
        task_manager.register_client(task_id, websocket)
        
        # Send initial state
        await websocket.send_json(task.model_dump())
        
        # Keep the connection alive and handle disconnection
        while True:
            try:
                await websocket.receive_text()
            except Exception:
                break
                
    finally:
        task_manager.unregister_client(task_id, websocket) 