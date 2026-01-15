from openai import OpenAI
from pathlib import Path

# === CONFIG ===
# <-- Replace with your actual OpenAI API key
API_KEY = "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"
OUTPUT_FILE = "test_tts.mp3"

# Initialize client
client = OpenAI(api_key=API_KEY)

print("Generating test audio with OpenAI TTS...")

# Generate speech (short test sentence)
response = client.audio.speech.create(
    model="tts-1",                  # high-quality model
    # one of the 6 voices (try "alloy", "echo", "fable", "onyx", "nova", "shimmer")
    voice="nova",
    input="Hello, this is a test of OpenAI TTS for the audiobook assignment. The rain is falling softly outside.",
    response_format="mp3"           # or "wav" if you prefer
)

# Save to file
response.stream_to_file(OUTPUT_FILE)
print(f"Success! Audio saved to: {OUTPUT_FILE}")
print("You can now open and play the file to check the voice quality.")
