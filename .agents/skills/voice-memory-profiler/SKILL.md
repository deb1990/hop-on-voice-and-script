---
name: voice-memory-profiler
description: >-
  Analyzes user-provided audio recordings, isolates the primary speaker, extracts comprehensive
  vocal delivery dynamics (pitch, tempo, pauses, emphasis, fillers, London Banglish syntax), and
  saves a persistent Voice & Delivery Blueprint to clone delivery for any future script.
---

# Voice Memory Profiler Skill

This skill guides the AI to analyze audio recordings provided by the user, isolate the primary speaker from secondary voices, extract a complete acoustic and linguistic delivery fingerprint, and store it into a persistent voice blueprint.

> [!NOTE]
> This skill is strictly for **Voice & Delivery Profiling**. It is script-agnostic. Its purpose is to understand exactly how the user speaks (tone, pauses, emphasis, rhythm, fillers, code-switching) so that any future script or voice synthesis can clone their delivery accurately.

---

## 1. Core Profile & Guardrails (STRICT)

- **Dialect Boundary:** Urban Kolkata Bengali (*Cholitobhasha* / চলিত ভাষা).
- **Prohibited Markers (ZERO TOLERANCE):** Strictly no East Bengal / Bangladeshi dialectal traits, vocabulary, or phonetics (avoid *পানি*, *দাওয়াত*, *আম্মা*, *করসি*, *খাইসি*; use *জল*, *নিমন্ত্রণ*, *মা*, *করেছি*, *খেয়েছি*).
- **Bengali Purist Standard:** Crisp, accurate, uncorrupted standard Bengali enunciation and proper grammatical verb conjugations.
- **London Diaspora Banglish:** Natural, sophisticated bilingual code-switching between cultured Kolkata Bengali and English concepts.
- **AI Interaction Language:** Always communicate with the user in **English**.

---

## 2. Step-by-Step Profiling Pipeline

When the user provides one or more audio files:

### Step 1: Ingest & Speaker Diarization (Isolation)
1. Locate the audio file(s) (`.m4a`, `.mp3`, `.wav`, etc.) at the path specified by the user.
2. If multiple speakers exist:
   - Identify the **Primary Speaker**: The user is the dominant speaker with the **majority of talk time / speaking turns**.
   - **Filter Out Secondary Speakers**: Discard segments from interviewers, conversation partners, or background interjections.
   - Keep only the primary speaker's segments for analysis.

### Step 2: Acoustic & Delivery Extraction
Examine the primary speaker's audio across these vocal dynamics:
1. **Pacing & Tempo:**
   - Measure base speech tempo (words / syllables per minute).
   - Identify acceleration points (e.g., eager explanations) vs. deceleration points (e.g., landing an important thesis).
2. **Pause Architecture:**
   - Detect **micro-pauses** (comma breaks, rhythmic breath pauses ~200-350ms).
   - Detect **macro-pauses** (thought transitions, deliberate rhetorical beats ~600-900ms).
   - Note breath patterns (e.g., audible inhales before key assertions).
3. **Pitch & Intonation Contours:**
   - Identify baseline pitch register.
   - Map question / validation inflection (e.g., rising pitch on *তাই না?*, *বুঝলেন তো?*).
   - Map conclusive inflection (e.g., falling cadence on definitive statements).
4. **Stress & Word Emphasis:**
   - How are emphasized words highlighted? (Volume increase, pitch jump, or deliberate vowel elongation).

### Step 3: Linguistic & Banglish Extraction
From the isolated speech, analyze:
1. **Fillers & Verbal Crutches:**
   - Catalog recurring hesitation sounds and filler phrases (*মানে*, *আসলে*, *যাই হোক*, *ব্যাপারটা হচ্ছে*, *you know*, *basically*).
2. **Banglish Code-Switching Architecture:**
   - What subjects trigger an English switch (e.g., technical concepts, modern business, adjectives)?
   - Suffix and particle attachment patterns (e.g., *point-টা*, *feel করা*, *actually*).
3. **Rhetorical Patterns:**
   - Opening hooks, transitional bridges, and conversational check-ins.

### Step 4: Persist into Voice Blueprint
Write the discovered metrics and traits into:
- `/Users/debarshibhaumik/.gemini/config/skills/voice-memory-profiler/resources/voice_memory_profile.md`

Populate all sections:
- Tempo and pacing modulation.
- Pause timings and breath rules.
- Pitch and intonation contours.
- Catalog of fillers and crutches with frequency and context.
- Banglish syntax rules and SSML / delivery markup tags.

### Step 5: Executive Delivery Summary
Provide the user with a concise summary in English:
- Key acoustic traits discovered (tempo, pause habits, pitch contours).
- Top fillers and signature Banglish code-switching patterns.
- Confirmation that the Voice & Delivery Blueprint has been saved.
