# Hop On Voice and Script

Tools, skills, and synthesis pipelines for Debarshi's **Hop On** travel documentaries.

## Contents

### 1. `scripts/`
- **`create_voice_profile.py`**: Registers a persistent replicated voice profile using `google-genai` SDK and Gemini 3.8 Flash TTS. Takes reference and consent WAV audio files and outputs a persistent `voice_id` (stored for 1 year with automatic renewal on use).
- **`gemini_voice_synth.py`**: CLI synthesis tool with paragraph chunking, speech metadata style anchoring, non-conflicting auto-numbering file exports, and direct WAV stitching.

### 2. `.agents/skills/` (Antigravity Auto-Discovery)
- **`hopon-scriptwriter`**: Authentically crafts spoken voiceover scripts in Debarshi's signature Kolkata Banglish style (pure spoken narration text, zero visual/production tags).

> **Note**: Placed inside `.agents/skills/` so `agy` (Google Antigravity) automatically discovers and registers it when opening this repository.

## Quickstart

### Environment Setup
```bash
export GEMINI_API_KEY="your_api_key_here"
```

### Create Voice Profile
```bash
python3 scripts/create_voice_profile.py \
  --reference path/to/reference.wav \
  --consent path/to/consent.wav \
  --display-name "Debarshi Voice Profile"
```

### Synthesize Script
```bash
python3 scripts/gemini_voice_synth.py \
  --voice-id "your_voice_id" \
  --file path/to/script.txt \
  --output output.wav
```
