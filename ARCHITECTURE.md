# Psychometric Audio Analysis - System Architecture

## Overview
The Psychometric Audio Analysis system is a full-stack web application that performs real-time audio analysis, including transcription, acoustic feature extraction, and paralinguistic analysis. The system uses a modern, scalable architecture with a React frontend and FastAPI backend.

## System Components

### 1. Frontend Architecture (`/frontend`)

#### Core Components
- **AudioAnalyzer**: Main container component orchestrating the analysis flow
- **FileUploader**: Handles audio file selection and upload
- **FeatureSelector**: UI for selecting analysis features
- **AudioVisualizer**: Displays waveform and real-time analysis
- **AnalysisResults**: Shows analysis results in an organized format

#### State Management
- Uses React hooks for local state management
- WebSocket connection for real-time updates
- File handling with HTML5 File API

#### UI/UX Features
- Black and white theme with green accents for progress
- Responsive grid layout
- Real-time progress indicators
- Chunked result display
- Interactive feature selection

### 2. Backend Architecture (`/backend`)

#### API Layer (`/app/api/v1`)
- **audio.py**: Main API routes
  - POST `/analyze`: Initiates audio analysis
  - GET `/status/{task_id}`: Checks analysis status
  - WS `/ws/{task_id}`: WebSocket endpoint for real-time updates

#### Core Services (`/app/services`)
- **AudioProcessor**: Core audio processing engine
  - Chunk-based processing
  - Feature extraction
  - Whisper integration for transcription
  
- **TaskManager**: Manages analysis tasks
  - Task creation and tracking
  - WebSocket client management
  - Progress monitoring

#### Data Models (`/app/schemas`)
- **AudioFeatureType**: Enum for feature types
  - TRANSCRIPTION
  - ACOUSTIC
  - PARALINGUISTIC

- **ChunkStatus**: Enum for processing status
  - PENDING
  - PROCESSING
  - COMPLETED
  - FAILED

### 3. Feature Processing Pipeline

#### Audio Processing Flow
1. File Upload
   - Temporary file storage
   - Format validation
   - Chunk preparation

2. Chunking Process
   - 60-second chunks by default
   - Overlap handling
   - Progress tracking

3. Feature Extraction
   - **Transcription (Whisper)**
     - Model: tiny.en
     - English-optimized
     - Real-time processing

   - **Acoustic Features**
     - MFCCs (Mel-frequency cepstral coefficients)
     - Pitch analysis
     - Formant frequencies
     - Energy metrics
     - Spectral features

   - **Paralinguistic Features**
     - Voice quality analysis
     - Emotional markers
     - Speech rate
     - Prosodic features

### 4. Real-time Communication

#### WebSocket Implementation
- Bi-directional communication
- Progress updates
- Chunk-wise result delivery
- Error handling

#### Data Flow
1. Client initiates analysis
2. Server creates task
3. WebSocket connection established
4. Real-time updates sent to client
5. Results displayed progressively

### 5. Dependencies

#### Frontend Dependencies
- React
- Chakra UI
- React Icons
- WebSocket client

#### Backend Dependencies
```python
# Web Framework
fastapi>=0.95.0
uvicorn[standard]>=0.15.0
websockets>=12.0

# Audio Processing
librosa>=0.9.1
numpy>=1.20.0
soundfile>=0.10.3
scipy>=1.12.0

# Machine Learning
scikit-learn>=1.4.0
openai-whisper==20231117
torch>=2.0.0
```

### 6. Security Considerations

- File validation and sanitization
- Temporary file cleanup
- WebSocket connection management
- Error handling and logging
- Resource usage monitoring

### 7. Performance Optimizations

- Chunk-based processing
- Asynchronous operations
- Efficient memory management
- Caching strategies
- Progress tracking

### 8. Deployment Requirements

#### System Requirements
- Python 3.8+
- Node.js 14+
- FFmpeg installation
- Sufficient RAM for audio processing
- CPU/GPU for Whisper model

#### Environment Setup
1. FFmpeg installation
2. Python virtual environment
3. Node.js and npm
4. Required system libraries

### 9. Future Extensibility

The architecture supports easy addition of:
- New feature types
- Different analysis models
- Additional visualization options
- Enhanced real-time capabilities
- Multiple language support

### 10. Error Handling

- Graceful failure recovery
- User-friendly error messages
- Detailed logging
- Task state management
- Connection recovery

## Development Workflow

1. Local Development
   ```bash
   # Backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload

   # Frontend
   npm install
   npm start
   ```

2. Testing
   - Unit tests
   - Integration tests
   - End-to-end testing
   - Performance testing

3. Deployment
   - Environment configuration
   - Dependency installation
   - Service startup
   - Monitoring setup 