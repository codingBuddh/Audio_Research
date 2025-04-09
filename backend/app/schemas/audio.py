from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum

class AudioFeatureType(str, Enum):
    MFCC = "mfcc"
    PITCH = "pitch"
    EMOTION_SCORES = "emotion_scores"
    SPEAKING_RATE = "speaking_rate"

class ChunkStatus(str, Enum):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class AudioChunk(BaseModel):
    chunk_id: int = Field(description="Unique identifier for the chunk")
    start_time: float = Field(description="Start time of the chunk in seconds")
    end_time: float = Field(description="End time of the chunk in seconds")
    status: ChunkStatus = Field(description="Current status of chunk processing")
    features: Optional[Dict[str, Any]] = Field(
        None,
        description="Extracted features for the chunk"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if processing failed"
    )

class AudioAnalysisRequest(BaseModel):
    feature_types: List[AudioFeatureType] = Field(
        description="List of audio features to extract",
        min_items=1
    )
    chunk_duration: float = Field(
        default=5.0,
        description="Duration of each audio chunk in seconds",
        gt=0
    )

class AudioAnalysisResponse(BaseModel):
    task_id: str = Field(description="Unique identifier for the analysis task")
    total_chunks: int = Field(description="Total number of chunks to process")
    chunks: List[AudioChunk] = Field(description="List of audio chunks and their analysis results")

class AudioFeatures(BaseModel):
    mfcc: Optional[List[float]] = None
    pitch: Optional[float] = None
    formants: Optional[List[float]] = None
    energy: Optional[float] = None
    zcr: Optional[float] = None
    spectral_features: Optional[Dict[str, float]] = None
    voice_onset_time: Optional[float] = None
    speaking_rate: Optional[float] = None
    pause_patterns: Optional[Dict[str, float]] = None
    emotion_scores: Optional[Dict[str, float]] = None 