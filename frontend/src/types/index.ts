export enum AudioFeatureType {
  MFCC = "mfcc",
  PITCH = "pitch",
  EMOTION_SCORES = "emotion_scores",
  SPEAKING_RATE = "speaking_rate",
}

export enum ChunkStatus {
  PROCESSING = "PROCESSING",
  COMPLETED = "COMPLETED",
  FAILED = "FAILED",
}

export interface AudioChunk {
  chunk_id: number
  start_time: number
  end_time: number
  status: ChunkStatus
  features?: any
  error?: string
}

export interface AudioAnalysisResponse {
  task_id: string
  total_chunks: number
  chunks: AudioChunk[]
} 