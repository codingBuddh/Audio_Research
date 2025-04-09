from fastapi import APIRouter, UploadFile, WebSocket, HTTPException, Form, File
from ...services.audio.task_manager import AudioTaskManager
from ...schemas.audio import AudioAnalysisRequest, AudioAnalysisResponse, AudioFeatureType
import os
import json
from tempfile import NamedTemporaryFile
import shutil
import logging

router = APIRouter()
task_manager = AudioTaskManager()
logger = logging.getLogger(__name__)

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
        logger.info(f"Received analysis request for file: {file.filename}")
        logger.info(f"Feature types: {feature_types}")
        
        # Parse feature types from JSON string
        try:
            feature_types_list = [AudioFeatureType(ft) for ft in json.loads(feature_types)]
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON for feature_types: {feature_types}")
            raise HTTPException(status_code=422, detail=f"Invalid feature types format: {str(e)}")
        except ValueError as e:
            logger.error(f"Invalid feature type value: {str(e)}")
            raise HTTPException(status_code=422, detail=f"Invalid feature type: {str(e)}")
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=422, detail="No file provided")
        
        # Create a unique filename to prevent conflicts
        file_extension = os.path.splitext(file.filename)[1]
        temp_file = NamedTemporaryFile(delete=False, suffix=file_extension, dir=UPLOAD_DIR)
        
        try:
            # Save the uploaded file
            with temp_file as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info(f"File saved successfully at: {temp_file.name}")
            
            # Create analysis task
            task_id = await task_manager.create_task(
                file_path=temp_file.name,
                feature_types=feature_types_list,
                chunk_duration=chunk_duration
            )
            
            logger.info(f"Analysis task created with ID: {task_id}")
            return task_manager.get_task_status(task_id)
            
        except Exception as e:
            # Clean up the temp file if task creation fails
            try:
                os.unlink(temp_file.name)
            except:
                pass
            raise e
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
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