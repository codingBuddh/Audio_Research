import asyncio
import uuid
from typing import Dict, List, Optional, Set
import librosa
import numpy as np
from fastapi import WebSocket
from ...schemas.audio import AudioAnalysisResponse, ChunkStatus
from .feature_extractor import FeatureExtractor
import logging

logger = logging.getLogger(__name__)

class AudioTaskManager:
    def __init__(self):
        self.tasks: Dict[str, AudioAnalysisResponse] = {}
        self.clients: Dict[str, Set[WebSocket]] = {}
        self.feature_extractor = FeatureExtractor()

    async def create_task(self, file_path: str, feature_types: List[str], chunk_duration: float = 5.0) -> str:
        """Create a new audio analysis task"""
        task_id = str(uuid.uuid4())
        
        try:
            # Load audio file
            audio, sr = librosa.load(file_path, sr=None)
            
            # Calculate chunk size in samples
            chunk_size = int(chunk_duration * sr)
            total_chunks = int(np.ceil(len(audio) / chunk_size))
            
            # Initialize task status
            self.tasks[task_id] = AudioAnalysisResponse(
                task_id=task_id,
                total_chunks=total_chunks,
                chunks=[{
                    "chunk_id": i,
                    "start_time": i * chunk_duration,
                    "end_time": min((i + 1) * chunk_duration, len(audio) / sr),
                    "status": ChunkStatus.PROCESSING,
                    "features": None,
                    "error": None
                } for i in range(total_chunks)]
            )
            
            # Start processing in background
            asyncio.create_task(self._process_audio(
                task_id=task_id,
                audio=audio,
                sr=sr,
                chunk_size=chunk_size,
                feature_types=feature_types
            ))
            
            return task_id
            
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            raise

    async def _process_audio(self, task_id: str, audio: np.ndarray, sr: int, 
                           chunk_size: int, feature_types: List[str]):
        """Process audio file in chunks"""
        task = self.tasks[task_id]
        
        for i in range(task.total_chunks):
            try:
                # Extract chunk
                start = i * chunk_size
                end = min(start + chunk_size, len(audio))
                chunk = audio[start:end]
                
                # Extract features
                features = self.feature_extractor.extract_features(chunk, feature_types)
                
                # Update chunk status
                task.chunks[i].status = ChunkStatus.COMPLETED
                task.chunks[i].features = features
                
            except Exception as e:
                logger.error(f"Error processing chunk {i}: {str(e)}")
                task.chunks[i].status = ChunkStatus.FAILED
                task.chunks[i].error = str(e)
            
            # Notify clients
            await self._notify_clients(task_id)
            
            # Small delay to prevent overloading
            await asyncio.sleep(0.1)

    def get_task_status(self, task_id: str) -> Optional[AudioAnalysisResponse]:
        """Get the current status of a task"""
        return self.tasks.get(task_id)

    def register_client(self, task_id: str, websocket: WebSocket):
        """Register a WebSocket client for task updates"""
        if task_id not in self.clients:
            self.clients[task_id] = set()
        self.clients[task_id].add(websocket)

    def unregister_client(self, task_id: str, websocket: WebSocket):
        """Unregister a WebSocket client"""
        if task_id in self.clients:
            self.clients[task_id].discard(websocket)
            if not self.clients[task_id]:
                del self.clients[task_id]

    async def _notify_clients(self, task_id: str):
        """Notify all clients about task updates"""
        if task_id in self.clients and task_id in self.tasks:
            dead_clients = set()
            
            for websocket in self.clients[task_id]:
                try:
                    await websocket.send_json(self.tasks[task_id].model_dump())
                except Exception:
                    dead_clients.add(websocket)
            
            # Remove dead clients
            for websocket in dead_clients:
                self.unregister_client(task_id, websocket) 