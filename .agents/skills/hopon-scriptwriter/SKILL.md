---
name: hopon-scriptwriter
description: >-
  Writes authentic, production-ready spoken voiceover (VO) scripts in Debarshi's signature Kolkata
  Banglish style using the persistent linguistic profile from user_linguistic_memory.md. Pure audio narration
  text with no visual tags or video production metadata. Proactively asks clarifying questions to tailor
  content, tone, and pacing.
---

# HOP ON Voiceover Scriptwriter Skill

This skill turns ideas, itineraries, travel notes, guides, or stories into complete, ready-to-read **Spoken Voiceover (VO) Scripts** matching Debarshi's authentic voice, cultured Kolkata *Cholitobhasha*, and natural Banglish code-switching patterns.

> [!IMPORTANT]
> **Single Source of Truth:**
> All dialect, grammar, prohibited forms, tone, Banglish rules, and signature vocabulary are defined in:
> `/Users/debarshibhaumik/.gemini/config/skills/voice-memory-profiler/resources/user_linguistic_memory.md`
>
> You **MUST read and strictly follow** `user_linguistic_memory.md` before generating any script.

---

## 1. Scope & Output Format (Pure Spoken Audio)

- **Natural Bengali Core (Avoid Artificial "Over-Banglishing"):**
  - **The backbone sentence structure must be authentic, natural, cultured Kolkata Bengali.**
  - **DO NOT randomly insert English words for everyday things that have natural Bengali words** (e.g., do NOT say *"Ami feel korchhilam happy"* or *"weather-ta chhilam enjoying"*).
  - **When English is used:** Only for modern/international concepts, specific proper nouns, technical terms, destination landmarks, or natural prepositional pivots (*towards*, *through*, *via*, *which is...*).
  - **Avoid awkward hybrid verbs:** Use real Bengali verbs (*dekhte pelam*, *chole elam*, *shuru korlam*, *katie*) rather than forcing English words with *-kora* everywhere.
- **Strict Typography Requirement (English Alphabet Only):**
  - **Always write scripts 100% in the English / Latin alphabet (Romanized Bengali / phonetic English characters).**
  - **Never use Bengali script (বাংলা হরফ).** The entire narration text must be phonetically readable in English letters (e.g., *"Ami Debarshi aar amar wife Poulomi..."*, *"Tai hop on with us on our journey..."*).
- **Pure Spoken Narration Only:** Write **only** the words to be spoken into the microphone.
- **Zero Video / Visual Metadata:** Strictly **no** visual directions, B-roll notes, drone cue tags, editing markers, or camera instructions. How the audio is used or edited is outside this skill's scope.
- **Mode A (Voiceover):** Polished, measured, cultured Kolkata *Cholitobhasha*. Zero hesitation fillers (*mane*, *hochhe*, *holo hochhe*, *actually* are strictly forbidden). Copula is **holo**.
- **No Format / Transit Assumptions:** Never assume driving, road trips, or specific video structures. The subject matter and travel mode come entirely from the user.

---

## 2. Interactive Clarification Workflow

Before drafting, if key narrative details or preferences are unspecified, ask concise clarifying questions:
1. **Subject & Narrative Arc:** What places, history, facts, or stories do you want to cover?
2. **Tone & Depth:** Quick overview guide vs. detailed, immersive narration?
3. **Channel Intro:** Do you want the standard HOP ON bio intro included at the start, or jump straight into the topic?

*(If the user provides full instructions or asks for direct generation, proceed straight to drafting without asking.)*

---

## 3. Script Presentation

Present the script with clean section headers and readable paragraphs ready to record:

```markdown
# [Title / Guide Name]

### 1. Opening Hook
[Spoken narration text]

### 2. [Topic / Location / Section]
[Spoken narration text]

### 3. [Next Topic / Transition]
[Spoken narration text]

...

### [Final Section]. Closing
[Spoken narration text]
```
