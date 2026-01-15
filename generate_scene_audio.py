from openai import OpenAI
from pathlib import Path
import json
import os
import time
from datetime import timedelta
from pydub import AudioSegment

# Tell pydub exactly where ffmpeg and ffprobe are
import pydub.utils
# Force pydub to use the exact paths (more reliable)
from pydub.utils import which
which('ffmpeg')  # dummy call to load utils
which('ffprobe')

pydub.utils.which = lambda x: {
    'ffmpeg': r"C:\ffmpeg\ffmpeg-2026-01-07-git-af6a1dd0b2-full_build\ffmpeg-2026-01-07-git-af6a1dd0b2-full_build\bin\ffmpeg.exe",
    'ffprobe': r"C:\ffmpeg\ffmpeg-2026-01-07-git-af6a1dd0b2-full_build\ffmpeg-2026-01-07-git-af6a1dd0b2-full_build\bin\ffprobe.exe",
}.get(x, None)

# === CONFIG ===
# <-- Replace with your actual OpenAI API key
API_KEY = "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"
INPUT_JSON = "output/audio_script.json"
OUTPUT_DIR = "audio"
SCENE_INDEX = 0  # Change to 1 or 2 if you want a different scene

# Voice mapping – EDIT THIS to match your exact speaker_ids from audio_script.json
VOICE_MAP = {
    "spk_narrator": "nova",     # Warm female narrator
    "spk_mira": "shimmer",      # Youthful female
    "spk_jonah": "onyx",        # Deep male
    # Add more if your JSON has extra speakers, e.g.:
    # "spk_003": "fable",
}

# Initialize OpenAI client
client = OpenAI(api_key=API_KEY)

# Create output directory and debug
os.makedirs(OUTPUT_DIR, exist_ok=True)
print("Current working directory:", os.getcwd())
print("Audio directory exists?", os.path.exists(OUTPUT_DIR))
print("Can write to audio folder?", os.access(OUTPUT_DIR, os.W_OK))

# Quick test write to confirm permissions
test_file = Path(OUTPUT_DIR) / "write_test.txt"
try:
    with open(test_file, "w") as f:
        f.write("Test write successful")
    print("Write test succeeded! Deleting test file.")
    os.remove(test_file)
except Exception as e:
    print("Write test FAILED:", e)
    print("Fix permissions or run terminal as administrator.")
    exit(1)

# Load the JSON
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

# Get the selected scene
scenes = data.get("scenes", [])
if SCENE_INDEX >= len(scenes):
    print(
        f"Error: Only {len(scenes)} scenes found. Max index: {len(scenes)-1}")
    exit(1)

scene = scenes[SCENE_INDEX]
scene_id = scene["scene_id"]
print(f"\nGenerating audio for scene: {scene_id}")

output_mp3 = Path(OUTPUT_DIR) / f"{scene_id}.mp3"
temp_files = []
all_audio_clips = []

current_time = 0

for event in scene["timeline"]:
    if event["event_type"] == "line":
        speaker_id = event["speaker_id"]
        text = event["text"].strip()
        emotion = event["emotion"]
        delivery = event["delivery"]

        voice = VOICE_MAP.get(speaker_id)
        if not voice:
            print(f"Warning: No voice mapped for {speaker_id}. Skipping.")
            continue

        # Simple emotion/delivery markup for OpenAI TTS
        if emotion in ["angry", "surprised", "excited"]:
            if delivery["volume"] == "loud":
                text = text.upper()
            else:
                text = f"*{text}*"
        elif emotion == "whispering":
            text = f"...{text}..."
        elif emotion in ["sad", "fearful", "tired"]:
            text = f"...{text}..."

        pause_sec = delivery["pause_after_ms"] / 1000
        if pause_sec > 0:
            text += f"   " * int(pause_sec * 2)  # rough pause simulation

        print(f"Generating line: {speaker_id} ({voice}): {text[:60]}...")

        try:
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                response_format="mp3"
            )

            temp_path = Path(OUTPUT_DIR) / f"temp_{len(temp_files)}.mp3"
            temp_files.append(temp_path)

            with open(temp_path, "wb") as f:
                f.write(response.content)

            print(f"Saved temp file: {temp_path}")
            all_audio_clips.append(temp_path)

            # Estimate time advance
            words = len(text.split())
            current_time += max(1, words / 2.5) + pause_sec

        except Exception as e:
            print(f"TTS failed for this line: {e}")
            continue

        time.sleep(1.5)  # Avoid rate limit

    elif event["event_type"] == "pause":
        pause_sec = event.get("pause_after_ms", 1000) / 1000 or 1
        current_time += pause_sec
        print(f"Pause: {pause_sec}s")

print(f"Estimated scene duration: {timedelta(seconds=int(current_time))}")

# Concatenate with pydub
if all_audio_clips:
    combined = AudioSegment.empty()
    for clip in all_audio_clips:
        combined += AudioSegment.from_mp3(clip)

    combined.export(str(output_mp3), format="mp3")
    print(f"\nSuccess! Full scene audio saved to: {output_mp3}")
    print("File size:", output_mp3.stat().st_size, "bytes")

    # Optional: clean up temp files
    # for temp in temp_files:
    #     os.remove(temp)
    # print("Temp files cleaned up.")
else:
    print("No audio clips generated – check errors above.")

print("Done. Play the file to verify.")
