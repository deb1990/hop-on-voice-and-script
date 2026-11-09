#!/usr/bin/env python3
"""CLI tool for custom voice replication and speech synthesis with Gemini models.

This script uses Google's `google-genai` SDK to:
1. Replicate a custom speaker voice using reference audio and consent recordings.
2. Synthesize multilingual speech using the `gemini-3.8-flash-tts` model and the
   replicated voice profile.
"""

from __future__ import annotations

import argparse
import base64
import os
import sys
from pathlib import Path
from typing import Any, NoReturn

from google import genai
from google.genai import errors, types


def fail(message: str, exit_code: int = 1) -> NoReturn:
    """Print an error message to stderr and terminate execution.

    Args:
        message: Description of the error.
        exit_code: Process exit code (default: 1).
    """
    sys.stderr.write(f"Error: {message}\n")
    sys.exit(exit_code)


def validate_environment() -> str:
    """Validate that GEMINI_API_KEY is configured in the environment.

    Returns:
        The validated API key string.

    Raises:
        SystemExit: If GEMINI_API_KEY is unset or empty.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        fail(
            "GEMINI_API_KEY environment variable is missing or empty.\n"
            "Please export your API key before running this script:\n"
            "    export GEMINI_API_KEY=\"your_actual_api_key_here\""
        )
    return api_key


def encode_audio_file(file_path: Path) -> str:
    """Read a local audio file and return its content as a Base64-encoded string.

    Args:
        file_path: Path to the audio file on disk.

    Returns:
        Base64-encoded string of the file bytes.

    Raises:
        SystemExit: If the file is missing or unreadable.
    """
    if not file_path.exists():
        fail(f"Required audio file not found: {file_path.resolve()}")
    if not file_path.is_file():
        fail(f"Audio path is not a valid file: {file_path.resolve()}")

    try:
        data = file_path.read_bytes()
    except OSError as err:
        fail(f"Failed to read file '{file_path}': {err}")

    if not data:
        fail(f"Audio file '{file_path}' is empty (0 bytes).")

    return base64.b64encode(data).decode("utf-8")


def replicate_voice(
    client: genai.Client,
    reference_path: Path,
    consent_path: Path,
    display_name: str = "Bilingual Voice Profile",
) -> str:
    """Create a replicated voice profile with Google GenAI.

    Args:
        client: Initialized genai.Client instance.
        reference_path: Path to the reference audio WAV file.
        consent_path: Path to the consent audio WAV file.
        display_name: Display name for the replicated voice.

    Returns:
        The persistent voice identifier string (`voice_id`).

    Raises:
        SystemExit: If voice creation fails.
    """
    print(f"Reading reference audio from: {reference_path.resolve()}")
    ref_b64 = encode_audio_file(reference_path)

    print(f"Reading consent audio from: {consent_path.resolve()}")
    consent_b64 = encode_audio_file(consent_path)

    print("Registering replicated voice profile with client.voices.create()...")
    voice_payload: dict[str, Any] = {
        "type": "replicated",
        "display_name": display_name,
        "model": "gemini-3.8-flash-tts",
        "replicated": {
            "source_audio": {
                "mime_type": "audio/wav",
                "data": ref_b64,
            },
            "consent_audio": {
                "mime_type": "audio/wav",
                "data": consent_b64,
            },
        },
    }

    try:
        voice_profile = client.voices.create(
            store=True,
            voice=voice_payload,
        )
    except (errors.APIError, errors.ClientError, errors.ServerError) as err:
        fail(f"Google GenAI API voice replication error: {err}")
    except Exception as err:
        fail(f"Unexpected error creating replicated voice profile: {err}")

    voice_id = getattr(voice_profile, "id", None) or getattr(voice_profile, "key", None)
    if not voice_id:
        fail(f"API response did not return a valid voice identifier: {voice_profile}")

    print(f"\n[VOICE PROFILE CREATED] voice_id: {voice_id}\n")
    return str(voice_id)


class _ReplicatedVoiceAccessor:
    """Descriptor proxy to expose `voice_id` on `speech_config.voice_config.replicated_voice`."""

    def __init__(self, voice_config: types.VoiceConfig) -> None:
        self._voice_config = voice_config

    @property
    def voice_id(self) -> str | None:
        return self._voice_config.voice

    @voice_id.setter
    def voice_id(self, value: str) -> None:
        self._voice_config.voice = value


# Dynamically attach replicated_voice property to types.VoiceConfig
types.VoiceConfig.replicated_voice = property(  # type: ignore[assignment]
    lambda self: _ReplicatedVoiceAccessor(self)
)


def get_non_conflicting_path(target_path: Path) -> Path:
    """Return a non-conflicting path by appending (1), (2), etc. if the file exists.

    Args:
        target_path: Desired target file path.

    Returns:
        Original path if it does not exist, or an incremented variant.
    """
    if not target_path.exists():
        return target_path

    parent = target_path.parent
    stem = target_path.stem
    suffix = target_path.suffix
    counter = 1

    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


import io
import re
import wave


def clean_markdown_text(text: str) -> str:
    """Strip markdown formatting (bold, italics, asterisks) while preserving text."""
    # Remove markdown bold/italics like **word** or *word*
    cleaned = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", text)
    # Remove remaining stray asterisks or underscores
    cleaned = re.sub(r"[\*_]{2,}", "", cleaned)
    # Normalize multiple whitespaces and newlines
    lines = [re.sub(r"[ \t]+", " ", line.strip()) for line in cleaned.splitlines()]
    return "\n".join(lines).strip()


def split_into_paragraphs(text: str) -> list[str]:
    """Split text into distinct non-empty paragraphs for chunked synthesis."""
    raw_paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not raw_paras:
        # Fallback to single line chunks if no double newlines
        raw_paras = [line.strip() for line in text.splitlines() if line.strip()]
    return raw_paras if raw_paras else [text.strip()]


def concatenate_wav_chunks(wav_bytes_list: list[bytes], pause_ms: int = 350) -> bytes:
    """Concatenate multiple WAV byte streams with a natural silence pause between them."""
    if not wav_bytes_list:
        return b""
    if len(wav_bytes_list) == 1:
        return wav_bytes_list[0]

    output_io = io.BytesIO()
    out_wave: wave.Wave_write | None = None
    silence_frames: bytes = b""

    for chunk in wav_bytes_list:
        with wave.open(io.BytesIO(chunk), "rb") as in_w:
            params = in_w.getparams()
            frames = in_w.readframes(in_w.getnframes())

            if out_wave is None:
                out_wave = wave.open(output_io, "wb")
                out_wave.setparams(params)
                num_silence_samples = int(params.framerate * (pause_ms / 1000.0)) * params.nchannels
                silence_frames = b"\x00" * (num_silence_samples * params.sampwidth)
            else:
                out_wave.writeframes(silence_frames)
            out_wave.writeframes(frames)

    if out_wave is not None:
        out_wave.close()

    return output_io.getvalue()


def _synthesize_single_chunk(
    client: genai.Client,
    text: str,
    voice_id: str,
    model_name: str = "gemini-3.8-flash-tts",
    style_prompt: str = (
        "authentic London and Kolkata Banglish travel documentary narrator. "
        "Natural Indian-Bengali conversational English cadence. "
        "Strictly non-rhotic, zero American accent, zero American twang. "
        "Pronounce English words with warm, casual urban Kolkata-British bilingual phonetics."
    ),
) -> bytes:
    """Generate audio for an individual paragraph chunk with style-metadata anchor."""
    speech_config = types.SpeechConfig(
        voice_config=types.VoiceConfig(voice=voice_id)
    )
    speech_config.voice_config.replicated_voice.voice_id = voice_id

    config = types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=speech_config,
    )

    # Attach speech_metadata style to ensure the model maintains the speaker's
    # authentic bilingual accent throughout English loanwords and proper nouns
    content_part = types.Part(
        text=text,
        speech_metadata=types.SpeechMetadata(style=style_prompt),
    )

    generate_fn = getattr(client, "generate_content", None) or client.models.generate_content
    response = generate_fn(
        model=model_name,
        contents=types.Content(role="user", parts=[content_part]),
        config=config,
    )

    audio_bytes: bytes | None = None
    if getattr(response, "candidates", None):
        for candidate in response.candidates:
            content = getattr(candidate, "content", None)
            if not content or not getattr(content, "parts", None):
                continue
            for part in content.parts:
                inline_data = getattr(part, "inline_data", None)
                if inline_data and getattr(inline_data, "data", None):
                    raw_data = inline_data.data
                    if isinstance(raw_data, str):
                        audio_bytes = base64.b64decode(raw_data)
                    else:
                        audio_bytes = bytes(raw_data)
                    break
            if audio_bytes:
                break

    if not audio_bytes:
        fail(f"Audio generation failed for chunk: '{text[:40]}...'")

    return audio_bytes


def synthesize_speech(
    client: genai.Client,
    text: str,
    voice_id: str,
    output_path: Path,
    model_name: str = "gemini-3.8-flash-tts",
) -> None:
    """Synthesize speech using paragraph chunking to preserve voice identity throughout.

    Args:
        client: Initialized genai.Client instance.
        text: Text string to synthesize.
        voice_id: Active replicated voice ID.
        output_path: Target path for the output audio file.
        model_name: Target Gemini model identifier (default: `gemini-3.8-flash-tts`).

    Raises:
        SystemExit: If generation fails or no audio stream is returned.
    """
    clean_text = clean_markdown_text(text)
    paragraphs = split_into_paragraphs(clean_text)

    print(f"Synthesizing speech with model '{model_name}'...")
    print(f"Active Voice ID: {voice_id}")
    print(f"Total paragraphs to synthesize: {len(paragraphs)}")

    chunk_audio_list: list[bytes] = []

    for idx, para in enumerate(paragraphs, start=1):
        print(f"\n[Chunk {idx}/{len(paragraphs)}] Synthesizing ({len(para)} chars):")
        print(f"  \"{para[:70]}...\"" if len(para) > 70 else f"  \"{para}\"")
        try:
            chunk_audio = _synthesize_single_chunk(
                client=client,
                text=para,
                voice_id=voice_id,
                model_name=model_name,
            )
            chunk_audio_list.append(chunk_audio)
        except (errors.APIError, errors.ClientError, errors.ServerError) as err:
            fail(f"Google GenAI API audio generation error on chunk {idx}: {err}")
        except Exception as err:
            fail(f"Network or request failure on chunk {idx}: {err}")

    # Concatenate all paragraph audio chunks with natural pauses
    print("\nStitching audio segments with natural pauses...")
    audio_bytes = concatenate_wav_chunks(chunk_audio_list, pause_ms=350)

    # Ensure output does not overwrite existing files by auto-incrementing
    final_output_path = get_non_conflicting_path(output_path)
    if final_output_path != output_path:
        print(f"File '{output_path.name}' already exists. Saving as '{final_output_path.name}' instead.")

    # Write binary byte stream directly to the target output file
    try:
        final_output_path.parent.mkdir(parents=True, exist_ok=True)
        final_output_path.write_bytes(audio_bytes)
    except OSError as err:
        fail(f"Failed to write audio output to '{final_output_path}': {err}")

    print(f"\n[SUCCESS] Synthesized audio successfully written to: {final_output_path.resolve()} ({len(audio_bytes)} bytes)")


def parse_arguments(args: list[str] | None = None) -> argparse.Namespace:
    """Parse and return command-line arguments.

    Args:
        args: Optional raw argument list (defaults to sys.argv[1:]).

    Returns:
        Parsed Namespace object.
    """
    default_text = "আমি আজকে office-এ যাওয়ার পথে heavy traffic-এ আটকে গিয়েছিলাম, so I will be late for the meeting."

    parser = argparse.ArgumentParser(
        description="CLI tool to replicate custom voices and synthesize speech with Gemini 3.8 Flash TTS.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--reference",
        type=Path,
        default=Path("reference.wav"),
        help="Path to reference audio WAV file.",
    )
    parser.add_argument(
        "--consent",
        type=Path,
        default=Path("consent.wav"),
        help="Path to consent audio WAV file.",
    )
    parser.add_argument(
        "--text",
        type=str,
        default=None,
        help="Text string to synthesize.",
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=None,
        help="Path to a text file (.txt, .md) containing the script to synthesize.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output.mp3"),
        help="Target path for the output audio file.",
    )
    parser.add_argument(
        "--voice-id",
        type=str,
        default=None,
        help="Optional existing Voice ID. If provided, skip profile creation and proceed straight to synthesis.",
    )

    return parser.parse_args(args)


def main() -> None:
    """Main CLI entrypoint."""
    args = parse_arguments()

    # Validate environment variable
    api_key = validate_environment()

    # Initialize client targeting v1alpha endpoint for speech synthesis and voice replication
    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(api_version="v1alpha"),
    )
    # Ensure client.generate_content is directly available on the client instance
    if not hasattr(client, "generate_content"):
        setattr(client, "generate_content", client.models.generate_content)

    # Step 1: Obtain or Replicate Voice ID
    if args.voice_id:
        voice_id = args.voice_id.strip()
        print(f"Using provided existing Voice ID: {voice_id} (skipping voice replication)")
    else:
        print("No --voice-id provided. Starting voice replication pipeline...")
        voice_id = replicate_voice(
            client=client,
            reference_path=args.reference,
            consent_path=args.consent,
            display_name="Bilingual Voice Profile",
        )

    # Determine text payload
    default_text = "আমি আজকে office-এ যাওয়ার পথে heavy traffic-এ আটকে গিয়েছিলাম, so I will be late for the meeting."
    if args.file:
        if not args.file.exists():
            fail(f"Input text file not found: {args.file.resolve()}")
        try:
            payload_text = args.file.read_text(encoding="utf-8").strip()
        except OSError as err:
            fail(f"Failed to read input file '{args.file}': {err}")
    elif args.text:
        payload_text = args.text.strip()
    else:
        payload_text = default_text

    if not payload_text:
        fail("Input text payload is empty.")

    # Step 2: Audio Generation
    synthesize_speech(
        client=client,
        text=payload_text,
        voice_id=voice_id,
        output_path=args.output,
        model_name="gemini-3.8-flash-tts",
    )


if __name__ == "__main__":
    main()
