# Casting / Voice Mapping for "The Copper Key" - Chapter 3

## Chosen TTS Provider

- OpenAI TTS (model: tts-1)
- Available voices: alloy, echo, fable, onyx, nova, shimmer

## Cast Mapping

(These are mapped to the speaker_ids from audio_script.json)

- **Narrator** (speaker_id: spk_narrator or similar)

  - Voice: **nova** (female, adult, warm and expressive tone)
  - Reason: Clear, engaging narration for descriptive passages; good for suspenseful storytelling.

- **Mira** (speaker_id: spk_mira or similar)

  - Voice: **shimmer** (female, young adult, bright and emotional)
  - Reason: Young female character; needs to convey surprise, fear, anger, and determination.

- **Jonah** (speaker_id: spk_jonah or similar)

  - Voice: **onyx** (male, adult, deep and calm)
  - Reason: Mysterious, confident male character; deep voice fits urgency and calm-under-pressure moments.

- (Add any other speakers if your JSON has more than these 3)

## Notes

- Voices are distinct: nova (warm female narration), shimmer (youthful female), onyx (deep male).
- Emotions are approximated via text markup (punctuation, CAPS for shouting, ellipses for pauses, etc.) since OpenAI TTS doesn't have direct emotion tags.
- Pace/volume: controlled via delivery fields in the JSON (we'll apply them in the next script).

This mapping ensures voice consistency across the scene(s).
