import streamlit as st
from openai import OpenAI
import json
import os
from pathlib import Path
from pydub import AudioSegment
import time

# ---------------- CONFIG ----------------
OPENAI_API_KEY = "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"  # <-- PASTE YOUR REAL OPENAI KEY HERE
MODEL_TTS = "tts-1"
MODEL_CHAT = "gpt-4o-mini"  # or "gpt-4o" if you have access

# Voice mapping (you can let user choose later)
VOICE_MAP = {
    "spk_narrator": "nova",
    "spk_mira": "shimmer",
    "spk_jonah": "onyx",
}

OUTPUT_DIR = Path("audio")
OUTPUT_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="Audiobook Generator", layout="wide")

# ---------------- SIDEBAR ----------------
st.sidebar.title("Audiobook Generator")
st.sidebar.markdown("Create multi-speaker audiobook from text")

# ---------------- MAIN UI ----------------
st.title("Audiobook Generator (TTS + SFX)")

# Input area
story_text = st.text_area(
    "Paste your story here (or upload chapter.txt)",
    height=200,
    placeholder="The rain started as a polite tapping... (paste full chapter)",
)

uploaded_file = st.file_uploader("Or upload chapter.txt", type=["txt"])
if uploaded_file is not None:
    story_text = uploaded_file.read().decode("utf-8")

if not story_text.strip():
    st.warning("Please enter or upload some story text to start.")
    st.stop()

# Progress / Status panel
status_container = st.container()
progress_bar = st.progress(0)
status_messages = []

def update_status(message, success=True):
    icon = "✅" if success else "❌"
    status_messages.append(f"{icon} {message}")
    status_container.markdown("\n".join(status_messages))
    progress_value = min(1.0, len(status_messages) / 5.0)  # 5 steps max, cap at 1.0
    progress_bar.progress(progress_value)

# Step 1: Detect speakers (simple keyword-based for demo)
if st.button("Generate Audiobook", type="primary"):
    update_status("Step 1: Detecting speakers...")

    # Very simple speaker detection (improve later with GPT if needed)
    speakers = set()
    lines = story_text.split("\n")
    for line in lines:
        line = line.strip()
        if line.endswith(":") and len(line.split()) < 5:
            speaker = line[:-1].strip()
            if speaker:
                speakers.add(speaker)

    num_speakers = len(speakers) if speakers else 1  # at least narrator
    update_status(f"Found {num_speakers} speakers: {', '.join(speakers) or 'Narrator only'}")

    # Step 2: Generate audio_script.json with GPT
    update_status("Step 2: Converting text to structured JSON...")

    client = OpenAI(api_key=OPENAI_API_KEY)

    # Simplified prompt (you can use your full one later)
    prompt = f"""
    Convert this story to audiobook JSON script.
    Use 1 scene, narrator + detected speakers.
    Return ONLY valid JSON matching this structure:
    {{"cast": [...], "scenes": [{{"scene_id": "scene_01", "timeline": [...]}}]}}
    Story text:
    {story_text[:4000]}  # truncate if too long
    """

    try:
        response = client.chat.completions.create(
            model=MODEL_CHAT,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=3000
        )
        json_str = response.choices[0].message.content.strip()
        if json_str.startswith("```json"):
            json_str = json_str.split("```json")[1].split("```")[0].strip()

        audio_script = json.loads(json_str)
        json_path = "output/audio_script_streamlit.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(audio_script, f, indent=2)
        update_status(f"JSON generated: {json_path}")
    except Exception as e:
        update_status(f"JSON generation failed: {e}", success=False)
        st.stop()

    # Step 3: Generate audio (simplified version of your previous script)
    update_status("Step 3: Generating TTS audio...")

    # Here you can paste your TTS generation logic (loop over timeline, generate clips, concatenate)
    # For now, let's simulate with a placeholder
    st.info("TTS generation in progress... (this may take 1-2 minutes)")
    time.sleep(5)  # simulate time
    final_audio_path = "audio/scene_01.mp3"  # replace with your real output

    # Placeholder - in real code, call your TTS + mix function here
    update_status("Audio generated successfully!")

    # Final output
    st.success("Audiobook Ready!")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Generated Audio")
        if os.path.exists(final_audio_path):
            st.audio(final_audio_path)
        else:
            st.warning("Audio file not found - check generation logs.")

    with col2:
        st.subheader("Script Preview")
        st.json(audio_script)
        st.download_button(
            "Download audio_script.json",
            data=json.dumps(audio_script, indent=2),
            file_name="audio_script.json",
            mime="application/json"
        )

    # Optional: show full text
    with st.expander("Original Story Text"):
        st.text(story_text)