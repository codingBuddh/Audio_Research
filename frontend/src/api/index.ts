import axios from 'axios'
import { AudioFeatureType, AudioAnalysisResponse } from '../types'

const API_BASE_URL = 'http://localhost:8000/api/v1'

export const analyzeAudio = async (
  file: File,
  featureTypes: AudioFeatureType[]
): Promise<AudioAnalysisResponse> => {
  const formData = new FormData()
  formData.append('file', file)
  
  // Convert feature types to strings and log the data
  const featureTypesStr = JSON.stringify(featureTypes.map(ft => ft.toString()))
  console.log('Sending feature types:', featureTypesStr)
  formData.append('feature_types', featureTypesStr)
  formData.append('chunk_duration', '60.0')

  try {
    const response = await axios.post<AudioAnalysisResponse>(
      `${API_BASE_URL}/analyze`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    console.log('Server response:', response.data)
    return response.data
  } catch (error: any) {
    console.error('API error:', error.response?.data || error.message)
    throw error
  }
}

export const connectToWebSocket = (taskId: string): WebSocket => {
  const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/${taskId}`)
  
  ws.onopen = () => {
    console.log('WebSocket connected')
  }
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
  }
  
  return ws
}

export const getTaskStatus = async (taskId: string): Promise<AudioAnalysisResponse> => {
  const response = await axios.get<AudioAnalysisResponse>(
    `${API_BASE_URL}/status/${taskId}`
  )
  return response.data
} 