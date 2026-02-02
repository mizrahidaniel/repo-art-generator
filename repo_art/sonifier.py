"""Generate music from repository data."""

import math
import struct
import wave
from typing import Dict, Any, List
from pathlib import Path


class MusicGenerator:
    """Generate music/audio from repository features."""
    
    def __init__(
        self,
        sample_rate: int = 44100,
        duration_per_commit: float = 0.1,
        base_frequency: float = 220.0  # A3
    ):
        self.sample_rate = sample_rate
        self.duration_per_commit = duration_per_commit
        self.base_frequency = base_frequency
    
    def generate(self, features: Dict[str, Any], output_path: str) -> None:
        """Generate audio file from repository features."""
        commits = features.get("commits", [])
        if not commits:
            self._write_silence(output_path, 1.0)
            return
        
        # Generate audio samples
        samples = self._generate_sonification(commits)
        
        # Write WAV file
        self._write_wav(output_path, samples)
    
    def _generate_sonification(self, commits: List[Dict[str, Any]]) -> List[float]:
        """Convert commits to audio samples.
        
        Strategy:
        - Each commit triggers a note
        - Additions = higher pitch
        - Deletions = lower pitch  
        - Activity = volume
        - Temporal spacing preserved
        """
        if not commits:
            return []
        
        # Calculate total duration
        timestamps = [c["timestamp"] for c in commits]
        min_time, max_time = min(timestamps), max(timestamps)
        time_range = max_time - min_time or 1
        
        # Total audio duration (scale to reasonable length)
        total_duration = min(60.0, len(commits) * self.duration_per_commit)
        total_samples = int(total_duration * self.sample_rate)
        
        # Initialize audio buffer
        audio = [0.0] * total_samples
        
        # Max activity for normalization
        max_activity = max(c["additions"] + c["deletions"] for c in commits) or 1
        
        # Generate note for each commit
        for commit in commits:
            # Time position in audio
            t_norm = (commit["timestamp"] - min_time) / time_range
            start_sample = int(t_norm * total_samples)
            
            # Calculate frequency based on additions/deletions ratio
            activity = commit["additions"] + commit["deletions"]
            if activity > 0:
                add_ratio = commit["additions"] / activity
                # More additions = higher pitch, more deletions = lower pitch
                frequency_multiplier = 0.5 + add_ratio * 1.5  # Range: 0.5x to 2x
            else:
                frequency_multiplier = 1.0
            
            frequency = self.base_frequency * frequency_multiplier
            
            # Volume based on activity
            volume = min(1.0, (activity / max_activity) * 0.5)
            
            # Note duration
            note_duration = self.duration_per_commit
            note_samples = int(note_duration * self.sample_rate)
            
            # Generate note with envelope (attack-decay-sustain-release)
            for i in range(note_samples):
                if start_sample + i >= total_samples:
                    break
                
                # Time within note
                t = i / self.sample_rate
                
                # ADSR envelope
                envelope = self._adsr_envelope(t, note_duration)
                
                # Generate sine wave with harmonics for richer sound
                sample = 0
                sample += math.sin(2 * math.pi * frequency * t)  # Fundamental
                sample += 0.3 * math.sin(2 * math.pi * frequency * 2 * t)  # 2nd harmonic
                sample += 0.1 * math.sin(2 * math.pi * frequency * 3 * t)  # 3rd harmonic
                
                # Apply envelope and volume
                sample *= envelope * volume
                
                # Add to audio buffer (mix)
                audio[start_sample + i] += sample * 0.3  # Scale to prevent clipping
        
        # Normalize to prevent clipping
        max_val = max(abs(s) for s in audio) or 1.0
        if max_val > 1.0:
            audio = [s / max_val for s in audio]
        
        return audio
    
    @staticmethod
    def _adsr_envelope(t: float, duration: float) -> float:
        """Generate ADSR envelope for note.
        
        Attack, Decay, Sustain, Release
        """
        attack_time = min(0.01, duration * 0.1)
        decay_time = min(0.02, duration * 0.2)
        release_time = min(0.05, duration * 0.3)
        sustain_level = 0.7
        
        if t < attack_time:
            # Attack: 0 -> 1
            return t / attack_time
        elif t < attack_time + decay_time:
            # Decay: 1 -> sustain
            progress = (t - attack_time) / decay_time
            return 1.0 - (1.0 - sustain_level) * progress
        elif t < duration - release_time:
            # Sustain: hold
            return sustain_level
        else:
            # Release: sustain -> 0
            progress = (t - (duration - release_time)) / release_time
            return sustain_level * (1.0 - progress)
    
    def _write_wav(self, output_path: str, samples: List[float]) -> None:
        """Write audio samples to WAV file."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with wave.open(output_path, 'w') as wav_file:
            # 1 channel (mono), 2 bytes per sample (16-bit)
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            
            # Convert float samples to 16-bit integers
            for sample in samples:
                # Clamp to [-1.0, 1.0] and scale to int16 range
                sample = max(-1.0, min(1.0, sample))
                int_sample = int(sample * 32767)
                wav_file.writeframes(struct.pack('<h', int_sample))
    
    def _write_silence(self, output_path: str, duration: float) -> None:
        """Write silent audio file."""
        samples = [0.0] * int(duration * self.sample_rate)
        self._write_wav(output_path, samples)
