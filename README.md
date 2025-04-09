# Psychometric Audio Analysis

A modern web application for advanced audio analysis, featuring real-time transcription, acoustic feature extraction, and paralinguistic analysis. Built with React, FastAPI, and Whisper AI.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- 🎤 **Real-time Audio Analysis**
  - Chunk-based processing for long audio files
  - Live progress tracking
  - WebSocket-based updates

- 🤖 **AI-Powered Transcription**
  - Whisper AI integration (tiny.en model)
  - Optimized for English language
  - High accuracy speech-to-text

- 📊 **Acoustic Feature Extraction**
  - MFCCs (Mel-frequency cepstral coefficients)
  - Pitch and formant analysis
  - Spectral characteristics
  - Energy metrics

- 🎭 **Paralinguistic Analysis**
  - Voice quality assessment
  - Emotional markers
  - Speech rate analysis
  - Prosodic feature extraction

## Prerequisites

- Python 3.8+
- Node.js 14+
- FFmpeg
- npm or yarn

## Installation

### Backend Setup

1. Install FFmpeg:
   ```bash
   # macOS
   brew install ffmpeg

   # Ubuntu/Debian
   sudo apt update && sudo apt install ffmpeg

   # Windows (using Chocolatey)
   choco install ffmpeg
   ```

2. Set up Python environment:
   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   .\venv\Scripts\activate

   # Install dependencies
   pip install -r backend/requirements.txt
   ```

3. Start the backend server:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

The application will be available at `http://localhost:5173`

## Usage

1. **Upload Audio**
   - Drag and drop or click to select an audio file
   - Supported formats: MP3, WAV, M4A, AAC, OGG

2. **Select Features**
   - Choose from Transcription, Acoustic, and Paralinguistic analysis
   - Multiple features can be selected simultaneously

3. **Analyze**
   - Click "Analyze Audio" to start processing
   - View real-time progress and results
   - Results are displayed per chunk with detailed metrics

## Project Structure

```
.
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── types/
│   │   └── api/
│   ├── package.json
│   └── vite.config.ts
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   └── schemas/
│   └── requirements.txt
│
└── README.md
```

## API Documentation

The backend API provides the following endpoints:

- `POST /api/v1/analyze` - Initialize audio analysis
- `GET /api/v1/status/{task_id}` - Check analysis status
- `WS /api/v1/ws/{task_id}` - WebSocket for real-time updates

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Style

- Backend follows PEP 8 guidelines
- Frontend uses ESLint and Prettier
- Run linters before committing:
  ```bash
  # Backend
  flake8 backend/

  # Frontend
  cd frontend
  npm run lint
  ```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI Whisper for transcription
- librosa for audio processing
- FastAPI for backend framework
- React and Chakra UI for frontend 