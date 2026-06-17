"""AcousticAgent — NBHF click detection for Yangtze finless porpoise.

Implements basic narrow-band high-frequency click detection (110-150kHz).
The Yangtze finless porpoise produces NBHF clicks distinct from other cetaceans.

Signal processing chain:
  raw_audio -> bandpass(110-150kHz) -> envelope -> threshold -> click_events
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List


@dataclass
class ClickEvent:
    timestamp_ms: float
    peak_frequency_hz: float
    duration_ms: float
    rms_amplitude: float
    snr_db: float


class NBHFDetector:
    """Narrow-Band High-Frequency click detector for finless porpoise."""

    def __init__(self, sample_rate: int = 500000,  # 500 kHz
                 freq_low: float = 110000, freq_high: float = 150000):
        self.sample_rate = sample_rate
        self.freq_low = freq_low
        self.freq_high = freq_high

    def detect(self, audio: np.ndarray, threshold_db: float = 10.0) -> List[ClickEvent]:
        """Detect NBHF clicks in raw audio signal.

        Args:
            audio: 1D numpy array of audio samples
            threshold_db: Detection threshold in dB above noise floor

        Returns:
            List of ClickEvent dataclass instances
        """
        # Step 1: Bandpass filter (110-150kHz for finless porpoise NBHF)
        filtered = self._bandpass_filter(audio)

        # Step 2: Hilbert envelope
        envelope = np.abs(self._hilbert(filtered))

        # Step 3: Noise floor estimation (median of lower 50%)
        noise_floor = np.median(np.sort(envelope)[:len(envelope)//2])
        threshold = noise_floor * (10 ** (threshold_db / 20))

        # Step 4: Click event extraction
        events = self._extract_clicks(envelope, filtered, threshold)

        return events

    def _bandpass_filter(self, signal: np.ndarray) -> np.ndarray:
        """Simple bandpass using FFT."""
        n = len(signal)
        freqs = np.fft.rfftfreq(n, 1/self.sample_rate)
        spectrum = np.fft.rfft(signal)
        mask = (freqs >= self.freq_low) & (freqs <= self.freq_high)
        spectrum[~mask] = 0
        return np.fft.irfft(spectrum, n)

    def _hilbert(self, signal: np.ndarray) -> np.ndarray:
        """Hilbert transform via FFT."""
        n = len(signal)
        spectrum = np.fft.rfft(signal)
        spectrum[1:] *= 2
        spectrum[0] = 0
        return np.fft.irfft(spectrum, n)

    def _extract_clicks(self, envelope: np.ndarray, filtered: np.ndarray,
                        threshold: float) -> List[ClickEvent]:
        """Extract individual click events from envelope."""
        above = envelope > threshold
        events = []
        start = None

        for i in range(len(above)):
            if above[i] and start is None:
                start = i
            elif not above[i] and start is not None:
                duration = (i - start) / self.sample_rate * 1000  # ms
                if 0.05 < duration < 2.0:  # NBHF clicks: 0.05-2ms
                    segment = filtered[start:i]
                    peak_freq = self.sample_rate * np.argmax(np.abs(np.fft.rfft(segment))) / len(segment)
                    rms = np.sqrt(np.mean(segment**2))
                    snr = 20 * np.log10(rms / (threshold / (10 ** (10/20))) + 1e-10)
                    events.append(ClickEvent(
                        timestamp_ms=start / self.sample_rate * 1000,
                        peak_frequency_hz=peak_freq,
                        duration_ms=duration,
                        rms_amplitude=rms,
                        snr_db=snr
                    ))
                start = None

        return events


def detect_porpoise_clicks(audio_path: str, **kwargs) -> dict:
    """Convenience function for porpoise-agent AcousticAgent."""
    import wave
    with wave.open(audio_path, 'r') as wf:
        audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        audio = audio / 32768.0  # Normalize

    detector = NBHFDetector(sample_rate=wf.getframerate())
    clicks = detector.detect(audio, **kwargs)

    return {
        "total_clicks": len(clicks),
        "click_rate_per_min": len(clicks) / (len(audio) / wf.getframerate() * 60),
        "mean_duration_ms": np.mean([c.duration_ms for c in clicks]) if clicks else 0,
        "mean_peak_freq_hz": np.mean([c.peak_frequency_hz for c in clicks]) if clicks else 0,
        "clicks": [{"t_ms": round(c.timestamp_ms, 1),
                     "freq_hz": round(c.peak_frequency_hz, 0),
                     "dur_ms": round(c.duration_ms, 3)}
                    for c in clicks[:20]]
    }
