import librosa
import numpy as np
from typing import Dict, List, Any, Optional
import logging
from ...schemas.audio import AudioFeatureType, AcousticFeatures, SpectralFeatures

logger = logging.getLogger(__name__)

class FeatureExtractor:
    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate

    def extract_features(self, audio_chunk: np.ndarray, feature_types: List[str]) -> Dict[str, Any]:
        """Extract requested features from the audio chunk"""
        features = {}
        
        try:
            for feature_type in feature_types:
                if feature_type == AudioFeatureType.ACOUSTIC:
                    features["acoustic"] = self._extract_acoustic_features(audio_chunk)
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

    def _extract_acoustic_features(self, audio_chunk: np.ndarray) -> AcousticFeatures:
        """Extract all acoustic features (Low-Level Descriptors)"""
        
        # 1. MFCCs
        mfccs = librosa.feature.mfcc(y=audio_chunk, sr=self.sample_rate, n_mfcc=13)
        mfcc_means = mfccs.mean(axis=1).tolist()

        # 2. Pitch (Fundamental Frequency)
        pitches, magnitudes = librosa.piptrack(y=audio_chunk, sr=self.sample_rate)
        pitch = float(pitches[magnitudes > 0.5].mean()) if len(pitches[magnitudes > 0.5]) > 0 else 0.0

        # 3. Formants (using linear prediction coefficients as proxy)
        lpc_coeffs = librosa.lpc(audio_chunk, order=8)
        formants = np.abs(np.roots(lpc_coeffs))
        formant_freqs = sorted([float(f * self.sample_rate / (2 * np.pi)) for f in formants if f < 1])[:3]
        
        # 4. Energy
        energy = float(np.sqrt(np.mean(audio_chunk**2)))

        # 5. Zero-Crossing Rate
        zcr = float(librosa.feature.zero_crossing_rate(audio_chunk)[0].mean())

        # 6. Spectral Features
        spectral = self._extract_spectral_features(audio_chunk)

        # 7. Voice Onset Time (VOT) - simplified estimation
        # Using the time between the burst (high energy) and the onset of voicing
        onset_env = librosa.onset.onset_strength(y=audio_chunk, sr=self.sample_rate)
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=self.sample_rate)
        vot = float(np.mean(np.diff(onsets))) if len(onsets) > 1 else None

        return AcousticFeatures(
            mfcc=mfcc_means,
            pitch=pitch,
            formants=formant_freqs,
            energy=energy,
            zcr=zcr,
            spectral=spectral,
            vot=vot
        )

    def _extract_spectral_features(self, audio_chunk: np.ndarray) -> SpectralFeatures:
        """Extract spectral features"""
        
        # Spectral Centroid
        centroid = float(librosa.feature.spectral_centroid(y=audio_chunk, sr=self.sample_rate).mean())
        
        # Spectral Bandwidth
        bandwidth = float(librosa.feature.spectral_bandwidth(y=audio_chunk, sr=self.sample_rate).mean())
        
        # Spectral Flux
        spec = np.abs(librosa.stft(audio_chunk))
        flux = float(np.mean(np.diff(spec, axis=1)))
        
        # Spectral Rolloff
        rolloff = float(librosa.feature.spectral_rolloff(y=audio_chunk, sr=self.sample_rate).mean())
        
        return SpectralFeatures(
            centroid=centroid,
            bandwidth=bandwidth,
            flux=flux,
            rolloff=rolloff
        )

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