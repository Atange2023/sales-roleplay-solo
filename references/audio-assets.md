# Audio and MIDI assets

## Lookup order

1. Resolve ID and variant in `assets/audio-manifest.json`.
2. Play the non-empty packaged MP3 at `file`.
3. If missing and the session explicitly permits network use, call dynamic TTS.
4. Otherwise display `display_text` and report a text fallback. Never claim it is a pre-generated voice.

`py scripts/tts_speak.py --play B1_why_zhous --offline --no-launch` must resolve the business-school file locally.

## Manifest contract

Every entry includes: `id`, `variant`, `role`, `role_name`, `scenario`, `display_text`, `spoken_text`, `file`, `fixed`, `source`, and `generation`.

- 145 entries use `source: v0.3-pre-generated` and preserve the original bytes in `audio/`, `audio3/`, and `audio4/`.
- v0.4 fixed system/outcome lines use `source: v0.4-windows-sapi-pre-generated`. They were generated before packaging with the local Microsoft Huihui Desktop zh-CN voice and converted locally to MP3.
- Spoken text may be shorter than display text for latency, but the manifest records both.

Regenerate the catalog with `py scripts/build_audio_manifest.py`. On a Windows machine with Huihui and ffmpeg, regenerate v0.4 fixed MP3s with `powershell -ExecutionPolicy Bypass -File scripts/generate_fixed_audio.ps1`.

Regenerate MIDI with `py scripts/generate_midi.py`. Required cues are boot, stage-clear, professional-exit, game-over, and achievement.