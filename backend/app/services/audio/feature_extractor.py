import librosa
import numpy as np
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class FeatureExtractor:
    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate

    def extract_features(self, audio_chunk: np.ndarray, feature_types: List[str]) -> Dict[str, Any]:
        """Extract requested features from the audio chunk"""
        features = {}
        
        try:
            for feature_type in feature_types:
                if feature_type == "mfcc":
                    features["mfcc"] = self._extract_mfcc(audio_chunk)
                elif feature_type == "pitch":
                    features["pitch"] = self._extract_pitch(audio_chunk)
                elif feature_type == "emotion_scores":
                    features["emotion_scores"] = self._extract_emotion_scores(audio_chunk)
                elif feature_type == "speaking_rate":
                    features["speaking_rate"] = self._extract_speaking_rate(audio_chunk)
        except Exception as e:
            logger.error(f"Error extracting features: {str(e)}")
            raise
            
        return features

    def _extract_mfcc(self, audio_chunk: np.ndarray, n_mfcc: int = 13) -> List[float]:
        """Extract Mel-frequency cepstral coefficients"""
        mfccs = librosa.feature.mfcc(y=audio_chunk, sr=self.sample_rate, n_mfcc=n_mfcc)
        return mfccs.mean(axis=1).tolist()

    def _extract_pitch(self, audio_chunk: np.ndarray) -> float:
        """Extract fundamental frequency (pitch)"""
        pitches, magnitudes = librosa.piptrack(y=audio_chunk, sr=self.sample_rate)
        pitch = float(pitches[magnitudes > 0.5].mean()) if len(pitches[magnitudes > 0.5]) > 0 else 0.0
        return pitch

    def _extract_emotion_scores(self, audio_chunk: np.ndarray) -> Dict[str, float]:
        """Extract emotion-related features (arousal and valence)"""
        # Calculate basic audio features that correlate with emotions
        spectral_centroid = librosa.feature.spectral_centroid(y=audio_chunk, sr=self.sample_rate).mean()
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_chunk, sr=self.sample_rate).mean()
        zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_chunk).mean()
        
        # Map these features to arousal and valence scores (simplified mapping)
        arousal = min(1.0, max(0.0, (spectral_centroid / 5000 + zero_crossing_rate * 100) / 2))
        valence = min(1.0, max(0.0, spectral_rolloff / 12000))
        
        return {
            "arousal": float(arousal),
            "valence": float(valence)
        }

    def _extract_speaking_rate(self, audio_chunk: np.ndarray) -> float:
        """Estimate speaking rate in syllables per second"""
        # Detect onsets as a proxy for syllables
        onset_env = librosa.onset.onset_strength(y=audio_chunk, sr=self.sample_rate)
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=self.sample_rate)
        
        # Calculate syllables per second
        duration = len(audio_chunk) / self.sample_rate
        speaking_rate = len(onsets) / duration if duration > 0 else 0.0
        
        return float(speaking_rate) 