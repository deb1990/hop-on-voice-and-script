#!/usr/bin/env python3
"""Standalone CLI script to create and register a replicated Gemini voice profile.

This script takes reference and consent audio WAV files, base64 encodes them,
and registers a persistent voice profile with Gemini via `client.voices.create(store=True)`.
The resulting `voice_id` is output to stdout for subsequent speech synthesis requests.
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
    """Print an error message to stderr and terminate execution."""
    sys.stderr.write(f"Error: {message}\n")
    sys.exit(exit_code)


def validate_environment() -> str:
    """Ensure GEMINI_API_KEY is available."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        fail(
            "GEMINI_API_KEY environment variable is missing or empty.\n"
            "Please export your API key before running this script:\n"
            "    export GEMINI_API_KEY=\"your_actual_api_key_here\""
        )
    return api_key


def encode_audio_file(file_path: Path) -> str:
    """Read a local audio file and return its content as a Base64 string."""
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Register a replicated voice profile in Gemini and output the Voice ID.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--reference",
        type=Path,
        default=Path("reference.wav"),
        help="Path to speaker reference audio WAV file (10-30s natural speech).",
    )
    parser.add_argument(
        "--consent",
        type=Path,
        default=Path("consent.wav"),
        help="Path to speaker consent audio WAV file.",
    )
    parser.add_argument(
        "--display-name",
        type=str,
        default="Bilingual Voice Profile",
        help="Human-readable label for the voice profile.",
    )
    args = parser.parse_args()

    api_key = validate_environment()

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(api_version="v1alpha"),
    )

    print(f"Reading reference audio: {args.reference.resolve()}")
    ref_b64 = encode_audio_file(args.reference)

    print(f"Reading consent audio: {args.consent.resolve()}")
    consent_b64 = encode_audio_file(args.consent)

    print("Registering custom voice profile via client.voices.create()...")
    voice_payload: dict[str, Any] = {
        "type": "replicated",
        "display_name": args.display_name,
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
        fail(f"Unexpected error during voice profile registration: {err}")

    voice_id = getattr(voice_profile, "id", None) or getattr(voice_profile, "key", None)
    if not voice_id:
        fail(f"API response did not return a valid voice identifier: {voice_profile}")

    print("\n" + "=" * 60)
    print("VOICE PROFILE SUCCESSFULLY CREATED")
    print("=" * 60)
    print(f"Voice ID     : {voice_id}")
    print(f"Display Name : {getattr(voice_profile, 'display_name', args.display_name)}")
    print(f"Expire Time  : {getattr(voice_profile, 'expire_time', '1 year from creation')}")
    print("=" * 60)
    print("\nYou can now synthesize audio anytime using this Voice ID:")
    print(f'python3 gemini_voice_synth.py --voice-id "{voice_id}" --text "Your text here"')


if __name__ == "__main__":
    main()
