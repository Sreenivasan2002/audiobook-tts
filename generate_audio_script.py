from openai import OpenAI
import json
import os

# === CONFIG ===
# <-- Replace with your actual OpenAI API key
API_KEY = "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"
CHAPTER_FILE = "chapter.txt"
OUTPUT_JSON = "output/audio_script.json"
# or "gpt-4o" if you have access (cheaper and fast for structured JSON)
MODEL = "gpt-4o-mini"

# Create output folder
os.makedirs("output", exist_ok=True)

# Read chapter text
with open(CHAPTER_FILE, "r", encoding="utf-8") as f:
    chapter_text = f.read().strip()

# === System Prompt (forces strict JSON) ===
system_prompt = """
You are a strict JSON generator. Output ONLY valid JSON. Nothing else.
No explanations, no markdown, no code fences, no comments, no trailing commas.
Use double quotes for all strings. Ensure the output exactly matches the schema.
Self-validate: the JSON must be parseable and follow all rules below.
"""

# === User Prompt (based exactly on assignment template + schema) ===
user_prompt = f"""
Convert the following chapter text into an audiobook-ready script.

HARD REQUIREMENTS:
- Output MUST be ONLY a single JSON object that strictly validates this schema.
- Start with {{ and end with }}. No extra text.
- Timestamps (t) must be non-decreasing within each scene.
- Each line text <= 220 chars; split long narration.
- 1-3 scenes, 2-5 speakers (narrator + characters).
- Include SFX/pauses where appropriate.
- Emotions from this list only: neutral, happy, sad, angry, surprised, fearful, whispering, excited, tired, serious.
- Delivery pace/volume from: slow/medium/fast and soft/normal/loud.
- Return ONLY the JSON.

SCHEMA:
{{
  "meta": {{
    "title": string (1-120 chars),
    "chapter_id": string (1-64 chars),
    "language": "en",
    "target_duration_seconds": integer (60-600)
  }},
  "cast": [
    {{
      "speaker_id": string (regex: spk_[a-z0-9_]{{2,24}}),
      "name": string (1-60 chars),
      "type": "narrator" or "character",
      "voice_profile": {{
        "age": "child"|"teen"|"adult"|"elder",
        "gender_presentation": "female"|"male"|"nonbinary"|"ambiguous",
        "tone": string (1-80 chars),
        "pace": "slow"|"medium"|"fast",
        "accent": string (0-60 chars),
        "notes": string (0-160 chars)
      }}
    }}
  ] (2-5 items),
  "scenes": [
    {{
      "scene_id": string (regex: scene_[0-9]{{2}}),
      "setting": string (1-120 chars),
      "ambience": {{
        "description": string (1-120 chars),
        "bgm_style": string (0-120 chars),
        "loop": boolean
      }},
      "timeline": [
        {{
          "t": number (>=0, <=600),
          "event_type": "line"|"sfx"|"pause",
          "speaker_id": string (if line, must match cast; else ""),
          "text": string (if line, 1-220 chars; else ""),
          "emotion": string (if line, from allowed list; else ""),
          "delivery": {{
            "pace": "slow"|"medium"|"fast",
            "volume": "soft"|"normal"|"loud",
            "pause_after_ms": integer (0-2000)
          }},
          "sfx": {{
            "name": string (if sfx),
            "description": string (1-120 chars if sfx),
            "suggested_asset": string (0-80 chars)
          }}
        }}
      ] (10-40 events per scene)
    }}
  ] (1-3 scenes),
  "rendering_notes": {{
    "mixing_guidance": [string] (2-5 items, 1-160 chars each),
    "provider_assumptions": [string] (1-4 items, 1-160 chars each)
  }}
}}

CONTENT:
- title: "The Copper Key"
- chapter_id: "chapter_3"
- target_duration_seconds: 300
- chapter_text: 
\"\"\"{chapter_text}\"\"\"

INSTRUCTIONS:
- Faithfully summarize the chapter into 1-3 scenes.
- Include narrator + at least 1-2 characters.
- Add SFX events (rain, footsteps, door slam, hum, etc.) with timestamps.
- Use pauses for drama.
- Return ONLY the JSON object.
"""

# Initialize OpenAI client
client = OpenAI(api_key=API_KEY)

print("Generating structured audio script with OpenAI GPT...")

# Call GPT for JSON
response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0.1,  # very low for strict structure
    max_tokens=4000
)

generated_text = response.choices[0].message.content.strip()

# Try to clean and save
try:
    # Remove possible markdown fences
    if generated_text.startswith("```json"):
        generated_text = generated_text.split(
            "```json")[1].split("```")[0].strip()
    elif generated_text.startswith("```"):
        generated_text = generated_text.split("```")[1].strip()

    data = json.loads(generated_text)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Success! Saved to: {OUTPUT_JSON}")
    print("Meta:", data.get("meta", {}))
    print("Number of scenes:", len(data.get("scenes", [])))
    print("Number of cast members:", len(data.get("cast", [])))
except json.JSONDecodeError as e:
    print("JSON parsing failed. Raw output saved to raw_script_output.txt")
    with open("raw_script_output.txt", "w", encoding="utf-8") as f:
        f.write(generated_text)
    print("Error:", e)
    print("Raw output first 500 chars:", generated_text[:500] + "...")
except Exception as e:
    print("Unexpected error:", e)
