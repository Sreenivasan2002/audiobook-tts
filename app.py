import streamlit as st
from openai import OpenAI
import json
import os
from pathlib import Path
import time
from datetime import datetime

# Hardcoded API key (for testing - remove or secure later)
OPENAI_API_KEY = "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"

# This MUST be the first Streamlit command
st.set_page_config(page_title="Audiobook Generator", layout="wide")

MODEL_CHAT = "gpt-4o-mini"
MODEL_TTS = "tts-1"

# Voice mapping (edit if needed)
VOICE_MAP = {
    "spk_narrator": "nova",
    "spk_mira": "shimmer",
    "spk_jonah": "onyx",
}

OUTPUT_DIR = Path("audio")
OUTPUT_DIR.mkdir(exist_ok=True)

# Session state
if 'status_steps' not in st.session_state:
    st.session_state.status_steps = []
if 'audio_path' not in st.session_state:
    st.session_state.audio_path = None
if 'json_path' not in st.session_state:
    st.session_state.json_path = None

# UI - all in one page
st.title("📖 Audiobook Generator - TTS")

st.markdown("Paste your story or upload a .txt file, then click **Generate Audiobook**.")

# Input
col_text, col_upload = st.columns([3, 1])

with col_text:
    story_text = st.text_area(
        "Paste story text",
        height=250,
        placeholder="The rain started as a polite tapping...",
        key="story_input"
    )

with col_upload:
    uploaded = st.file_uploader("Upload .txt", type=["txt"])
    if uploaded:
        story_text = uploaded.read().decode("utf-8")
        st.success("File uploaded!")

# Generate button
if st.button("Generate Audiobook 🎧", type="primary", disabled=not story_text.strip()):
    # Reset state
    st.session_state.status_steps = []
    st.session_state.audio_path = None
    st.session_state.json_path = None

    with st.spinner("Generating..."):
        # Step 1: Detect speakers
        st.session_state.status_steps.append("Detecting speakers...")
        speakers = set()
        for line in story_text.split("\n"):
            line = line.strip()
            if line.endswith(":") and len(line.split()) < 5:
                speakers.add(line[:-1].strip())
        num = len(speakers) if speakers else 1
        st.session_state.status_steps.append(f"Found {num} speaker(s): {', '.join(speakers) or 'Narrator only'}")

        # Step 2: Generate JSON
        st.session_state.status_steps.append("Generating structured JSON...")
        client = OpenAI(api_key=OPENAI_API_KEY)

        prompt = f"""
        Convert this story into an audiobook-ready JSON script.
        Return ONLY valid JSON. No markdown, no extra text.
        Use schema: {{"cast": [...], "scenes": [{{"scene_id": "scene_01", "timeline": [...]}}]}}
        Include narrator + characters, emotions, delivery, SFX cues.
        Story:
        {story_text[:8000]}
        """

        try:
            response = client.chat.completions.create(
                model=MODEL_CHAT,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=4000
            )
            json_str = response.choices[0].message.content.strip()
            if json_str.startswith("```json"):
                json_str = json_str.split("```json")[1].split("```")[0].strip()

            script = json.loads(json_str)

            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_path = f"output/script_{ts}.json"
            os.makedirs("output", exist_ok=True)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(script, f, indent=2)

            st.session_state.json_path = json_path
            st.session_state.status_steps.append("JSON created successfully!")
        except Exception as e:
            st.session_state.status_steps.append(f"JSON failed: {str(e)}")

        # Step 3: Generate audio (placeholder)
        st.session_state.status_steps.append("Generating audio...")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_path = f"audio/audiobook_{ts}.mp3"

        try:
            # Placeholder TTS - replace with your full TTS logic later
            response = client.audio.speech.create(
                model=MODEL_TTS,
                voice="nova",
                input=story_text[:1000],
                response_format="mp3"
            )
            with open(audio_path, "wb") as f:
                f.write(response.content)

            st.session_state.audio_path = audio_path
            st.session_state.status_steps.append("Audio ready!")
        except Exception as e:
            st.session_state.status_steps.append(f"Audio failed: {str(e)}")

        st.session_state.status_steps.append("Done!")
        st.rerun()

# Show progress & results
st.markdown("### Progress & Results")
if st.session_state.status_steps:
    for step in st.session_state.status_steps:
        st.markdown(step)

progress = min(1.0, len(st.session_state.status_steps) / 5.0)
st.progress(progress)

# Audio
if st.session_state.audio_path and os.path.exists(st.session_state.audio_path):
    st.markdown("### Generated Audio")
    st.audio(st.session_state.audio_path, format="audio/mp3")
    with open(st.session_state.audio_path, "rb") as f:
        st.download_button("Download MP3", f, file_name=Path(st.session_state.audio_path).name, mime="audio/mp3")

# Script
if st.session_state.json_path:
    st.markdown("### Generated Script")
    with open(st.session_state.json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    st.json(data)
    st.download_button("Download JSON", json.dumps(data, indent=2), file_name=Path(st.session_state.json_path).name)

# Original text
if 'story_text' in locals() and story_text:
    with st.expander("Original Story"):
        st.text(story_text)