import hashlib
import io
import os
import wave
from typing import Dict, Any, Optional
from google import genai
from google.genai import types

VOICE_CONFIGS: Dict[str, Dict[str, str]] = {
    # Deep menacing / Darth Vader-style / Calm don
    "dramatic": {
        "voice": "Charon",
        "instruction": "Say in a slow, deep, ominous, theatrical villain voice, with dramatic pauses: "
    },
    "don": {
        "voice": "Charon",
        "instruction": "Say in a calm, slow, cold, menacing don voice, with quiet calculated authority: "
    },
    # Joker-style chaotic / Comedy villain
    "chaotic": {
        "voice": "Puck",
        "instruction": "Say in a fast, chaotic, unpredictable, laughing villain voice: "
    },
    "comedy": {
        "voice": "Puck",
        "instruction": "Say in a flamboyant, hilarious, frustrated, expressive comedy villain voice: "
    },
    # Mass cinema villain / Gabbar-style / Thanos-style
    "mass": {
        "voice": "Orus",
        "instruction": "Say in a loud, firm, heavy build-up, commanding cinematic villain voice: "
    },
    "menace": {
        "voice": "Orus",
        "instruction": "Say in a gritty, mocking, booming, raw menacing villain voice: "
    },
    "inevitable": {
        "voice": "Orus",
        "instruction": "Say in a deep, stoic, philosophical, inevitable titan villain voice: "
    },
    "bollywood": {
        "voice": "Orus",
        "instruction": "Say in a melodramatic, booming, operatic, theatrical villain voice: "
    },
    # Dry sarcastic / Smooth smiling-killer
    "sarcastic": {
        "voice": "Sadachbia",
        "instruction": "Say in a dry, calm, sarcastic, deadpan villain voice with cold irony: "
    },
    "smiling_killer": {
        "voice": "Sadachbia",
        "instruction": "Say in a soft, slow, smiling, silky sarcastic villain voice: "
    },
    # HERO MODE (score >= 70)
    "hero": {
        "voice": "Orus",
        "instruction": "Say in a warm, proud, energetic, booming praising voice with swagger: "
    }
}

DEFAULT_CONFIG = {
    "voice": "Charon",
    "instruction": "Say in a slow, deep, menacing, theatrical villain voice, with dramatic pauses: "
}

# In-memory audio cache: hash -> wav bytes
_AUDIO_CACHE: Dict[str, bytes] = {}

def _pcm_to_wav(pcm_data: bytes, sample_rate: int = 24000, channels: int = 1, sampwidth: int = 2) -> bytes:
    wav_io = io.BytesIO()
    with wave.open(wav_io, "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sampwidth)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)
    return wav_io.getvalue()

def generate_villain_audio(text: str, language: str, villain_style: str, level: str = "easy") -> bytes:
    lvl = (level or "easy").lower().strip()
    max_words = 220 if lvl == "hard" else 180

    words = text.strip().split()
    if len(words) > max_words:
        clean_text = " ".join(words[:max_words])
    else:
        clean_text = text.strip()

    style_cfg = VOICE_CONFIGS.get(villain_style.lower(), DEFAULT_CONFIG)

    # Determine voice and instruction based on difficulty level
    if lvl == "hard":
        voice_to_use = "Orus"
        instruction = "Say loudly shouting, furious, intense, theatrical rage, dramatic pauses: "
    elif lvl == "moderate":
        voice_to_use = style_cfg["voice"]
        instruction = f"Say in an irritated, sarcastic, sharp {style_cfg['instruction'].replace('Say in a ', '').replace('Say in an ', '')}"
    else:
        voice_to_use = style_cfg["voice"]
        instruction = style_cfg["instruction"]

    cache_key = hashlib.sha256(f"{lvl}::{villain_style}::{language}::{clean_text}".encode("utf-8")).hexdigest()

    if cache_key in _AUDIO_CACHE:
        return _AUDIO_CACHE[cache_key]

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=api_key)

    # Prompt with English style instruction and native language text
    prompt = f"{instruction}{clean_text}"

    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice_to_use
                    )
                )
            )
        )
    )

    # Extract raw PCM bytes from the candidate part
    raw_pcm = None
    for candidate in response.candidates:
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    raw_pcm = part.inline_data.data
                    break
        if raw_pcm:
            break

    if not raw_pcm:
        raise RuntimeError("No audio data returned by Gemini TTS.")

    wav_bytes = _pcm_to_wav(raw_pcm, sample_rate=24000, channels=1, sampwidth=2)
    _AUDIO_CACHE[cache_key] = wav_bytes
    return wav_bytes

