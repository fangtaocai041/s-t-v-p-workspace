# Skill: detect-clicks

## Signature
`detect_clicks(audio_path: str, threshold_db: float = -134.0, bandpass: tuple[float,float] = (100000, 180000), sr_min: int = 500000) → ClickDetectionResult`

## Trigger
```python
WHEN intent IN [ACOUSTIC_ANALYSIS, CLICK_DETECTION]
  OR query MATCHES r"(click|脉冲|NBHF|窄带高频|回声定位|echolocation|PAM|detect)"
THEN activate()
```

## Input
```yaml
REQUIRED:
  audio_path: str                              # .wav or .flac file
OPTIONAL:
  threshold_db: float = -134.0                 # SPL detection threshold [ref: Akamatsu 2005]
  bandpass_low: float = 100000                 # Hz, [80000, 120000]
  bandpass_high: float = 180000                # Hz, [150000, 200000]
  sr_min: int = 500000                         # minimum sample rate for NBHF
```

## Steps
```python
# 1. Load + validate
y, sr = load_audio(audio_path)
IF sr < sr_min THEN
    RETURN error("SR too low for NBHF: need ≥{sr_min} Hz, got {sr} Hz")

# 2. Bandpass filter
from scipy.signal import butter, filtfilt
nyq = sr / 2
b, a = butter(N=4, Wn=[bandpass_low/nyq, bandpass_high/nyq], btype='band')
y_filt = filtfilt(b, a, y)

# 3. RMS energy
frame_length = 256, hop_length = 128
rms = librosa.feature.rms(y=y_filt, frame_length=frame_length, hop_length=hop_length)[0]
rms_db = 20 * log10(rms + 1e-10)

# 4. Threshold detection
above = rms_db > threshold_db
starts, ends = find_transitions(above)  # diff(above) == +1 / -1
n_clicks = min(len(starts), len(ends))

# 5. Click train extraction (ICI pattern matching)
click_times = starts * hop_length / sr
icis = diff(click_times)  # inter-click intervals
buzz_events = icis[icis < 0.010]  # ICI < 10ms → buzz
n_buzzes = len(buzz_events)

# 6. Feature extraction (18+ dims)
features = {
    "temporal":  {ici_mean, ici_std, duration, buzz_check},
    "spectral":  {peak_freq, center_freq, bandwidth_3db, start_freq, end_freq},
    "energy":    {spl_mean, spl_std, av_splr, sd_pi},
}

# 7. Classification
model = load_model("random_forest_v1.pkl")
FOR EACH click_train IN extracted_trains:
    label = model.predict(features(click_train))
    # label ∈ {regular_click, buzz, noise, vessel_noise}

RETURN {
    n_clicks: int, n_buzzes: int,
    foraging_index: float = n_buzzes / max(n_clicks, 1),
    click_trains: list[ClickTrain],
    features: dict,
}
```

## Decision Points
```python
IF SNR(rms_db) < 3.0
THEN flag(low_confidence, reason="SNR < 3 dB")

IF n_clicks == 0 AND threshold_db >= -140
THEN retry(threshold_db=threshold_db - 2, max_retries=5)

IF foraging_index > 0.3  # n_buzzes/n_clicks
THEN label("active_feeding")

IF false_positive_rate > 0.10
THEN adjust(threshold_db, step=+2, max=threshold_db + 6)

IF n_buzzes > 0
THEN compute_diel_pattern(buzz_events, bins=[dawn, day, dusk, night])
```

## Output Schema
```json
{
  "audio_path": "string",
  "samplerate": 0,
  "n_clicks": 0,
  "n_buzzes": 0,
  "foraging_index": 0.0,
  "threshold_db": -134.0,
  "bandpass_hz": [100000, 180000],
  "fpr_estimate": 0.0,
  "flags": ["low_confidence | active_feeding | high_fpr"],
  "click_trains": [{
    "start_time": 0.0,
    "end_time": 0.0,
    "mean_ici": 0.0,
    "n_clicks": 0,
    "buzz_ratio": 0.0,
    "label": "regular_click|buzz|noise|vessel_noise"
  }],
  "diel_pattern": {
    "dawn": 0, "day": 0, "dusk": 0, "night": 0
  }
}
```

## References
- Akamatsu et al. (2005) JASA — source level
- Kimura et al. (2010) JASA — A-tag density estimation method
- Fang et al. (2015) JASA — click feature parameters
- Wang et al. (2014) PLoS ONE — diel echolocation pattern
