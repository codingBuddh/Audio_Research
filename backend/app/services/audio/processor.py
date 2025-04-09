import librosa
import numpy as np
from typing import Dict, List, Optional
import soundfile as sf
from pydub import AudioSegment
import os
from ...schemas.audio import AudioFeatureType, AudioFeatures
import logging
import whisper
import torch
from pathlib import Path

class AudioProcessor:
    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate
        self.logger = logging.getLogger(__name__)
        # Initialize Whisper model
        self.whisper_model = whisper.load_model("tiny.en")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def load_audio_chunk(self, file_path: str, start_time: float, end_time: float) -> np.ndarray:
        """Load a specific chunk of audio file"""
        try:
            y, sr = librosa.load(file_path, sr=self.sample_rate, offset=start_time, duration=end_time-start_time)
            return y
        except Exception as e:
            self.logger.error(f"Error loading audio chunk: {str(e)}")
            raise

    def extract_features(self, audio_chunk: np.ndarray, feature_types: List[AudioFeatureType]) -> AudioFeatures:
        """Extract requested features from audio chunk"""
        features = AudioFeatures()
        
        try:
            if AudioFeatureType.ACOUSTIC in feature_types:
                features.mfcc = self._extract_mfcc(audio_chunk)
                features.pitch = self._extract_pitch(audio_chunk)
                features.formants = self._extract_formants(audio_chunk)
                features.energy = self._extract_energy(audio_chunk)
                features.zcr = self._extract_zcr(audio_chunk)
                features.spectral_features = self._extract_spectral_features(audio_chunk)

            if AudioFeatureType.PARALINGUISTIC in feature_types:
                features.emotion_scores = self._extract_emotion_features(audio_chunk)

            if AudioFeatureType.SPEAKER in feature_types:
                features.speaking_rate = self._extract_speaking_rate(audio_chunk)
                features.voice_onset_time = self._extract_voice_onset_time(audio_chunk)

            return features
        except Exception as e:
            self.logger.error(f"Error extracting features: {str(e)}")
            raise

    def _extract_mfcc(self, y: np.ndarray, n_mfcc: int = 13) -> List[float]:
        """Extract MFCCs from audio chunk"""
        mfccs = librosa.feature.mfcc(y=y, sr=self.sample_rate, n_mfcc=n_mfcc)
        return mfccs.mean(axis=1).tolist()

    def _extract_pitch(self, y: np.ndarray) -> float:
        """Extract pitch (fundamental frequency) from audio chunk"""
        pitches, magnitudes = librosa.piptrack(y=y, sr=self.sample_rate)
        return float(np.mean(pitches[magnitudes > np.max(magnitudes)*0.7]))

    def _extract_formants(self, y: np.ndarray) -> List[float]:
        """Extract formant frequencies using LPC"""
        # Simplified formant extraction using LPC
        frame_length = 2048
        hop_length = 512
        pre_emphasis = 0.97
        
        # Pre-emphasis filter
        y = np.append(y[0], y[1:] - pre_emphasis * y[:-1])
        
        # Extract formants using LPC
        lpc_coeffs = librosa.lpc(y, order=8)
        formants = np.abs(np.roots(lpc_coeffs))
        formants = formants[formants.imag >= 0]
        formants = sorted(formants.real)
        
        return formants[:3].tolist()  # Return first 3 formants

    def _extract_energy(self, y: np.ndarray) -> float:
        """Extract energy from audio chunk"""
        return float(np.sum(y**2))

    def _extract_zcr(self, y: np.ndarray) -> float:
        """Extract zero-crossing rate from audio chunk"""
        zcr = librosa.feature.zero_crossing_rate(y)
        return float(np.mean(zcr))

    def _extract_spectral_features(self, y: np.ndarray) -> Dict[str, float]:
        """Extract various spectral features"""
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=self.sample_rate)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=self.sample_rate)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=self.sample_rate)
        
        return {
            "centroid": float(np.mean(spectral_centroid)),
            "bandwidth": float(np.mean(spectral_bandwidth)),
            "rolloff": float(np.mean(spectral_rolloff))
        }

    def _extract_emotion_features(self, y: np.ndarray) -> Dict[str, float]:
        """Extract features related to emotional content"""
        # This is a simplified version. In practice, you'd want to use a trained model
        energy = np.mean(librosa.feature.rms(y=y))
        pitch_mean = np.mean(librosa.piptrack(y=y, sr=self.sample_rate)[0])
        
        # Simplified emotion scoring based on energy and pitch
        return {
            "arousal": float(energy),
            "valence": float(pitch_mean),
        }

    def _extract_speaking_rate(self, y: np.ndarray) -> float:
        """Estimate speaking rate"""
        # Simplified speaking rate estimation using energy peaks
        hop_length = 512
        onset_env = librosa.onset.onset_strength(y=y, sr=self.sample_rate, hop_length=hop_length)
        peaks = librosa.util.peak_pick(onset_env, 3, 3, 3, 5, 0.5, 10)
        
        duration = len(y) / self.sample_rate
        speaking_rate = len(peaks) / duration  # syllables per second
        return float(speaking_rate)

    def _extract_voice_onset_time(self, y: np.ndarray) -> float:
        """Estimate voice onset time"""
        # Simplified VOT estimation
        energy = librosa.feature.rms(y=y)
        onset_frames = librosa.onset.onset_detect(y=y, sr=self.sample_rate)
        if len(onset_frames) > 0:
            return float(onset_frames[0] * 512 / self.sample_rate)  # Convert frames to seconds
        return 0.0

    def process_chunk(self, audio_path: str, start_time: float, end_time: float, feature_types: List[AudioFeatureType]) -> Dict[str, Any]:
        """Process a chunk of audio and extract requested features"""
        try:
            # Load the audio chunk
            y, sr = librosa.load(audio_path, offset=start_time, duration=end_time-start_time)
            
            features = {}
            
            # Transcribe audio chunk if needed
            if AudioFeatureType.TRANSCRIPTION in feature_types:
                # Save temporary chunk for Whisper
                temp_chunk_path = f"temp_chunk_{start_time}_{end_time}.wav"
                librosa.output.write_wav(temp_chunk_path, y, sr)
                
                try:
                    # Transcribe with Whisper
                    result = self.whisper_model.transcribe(temp_chunk_path)
                    features['transcription'] = result["text"].strip()
                finally:
                    # Clean up temporary file
                    Path(temp_chunk_path).unlink(missing_ok=True)
            
            # Process acoustic features if needed
            if AudioFeatureType.ACOUSTIC in feature_types:
                features['acoustic'] = self._extract_acoustic_features(y, sr)
            
            # Process paralinguistic features if needed
            if AudioFeatureType.PARALINGUISTIC in feature_types:
                features['paralinguistic'] = self._extract_paralinguistic_features(y, sr)
            
            return features
            
        except Exception as e:
            raise Exception(f"Error processing chunk: {str(e)}")

    def _extract_acoustic_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract acoustic features from audio chunk"""
        # ... existing acoustic feature extraction code ...

    def _extract_paralinguistic_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract paralinguistic features from audio chunk"""
        # ... existing paralinguistic feature extraction code ... 