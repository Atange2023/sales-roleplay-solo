# Audio assets

`assets/audio-manifest.json` is the single catalog. It indexes all 145 inherited v0.3 MP3 files and 24 packaged fixed system/ending lines. Each record contains ID, role, scenario, display text, spoken text, file, fixed flag, source, and generation metadata.

Use local audio first. `scripts/tts_speak.py --play <ID> --offline` searches the complete catalog, including business-school IDs. Dynamic TTS is fallback only and may require network access. Fixed lines and cue audio must work without network.

The five retro cues are boot, stage-clear, professional-exit, game-over, and achievement. MIDI sources live in `assets/midi/`; playable offline WAV fallbacks live in `assets/cues/`. `scripts/generate_midi.py` and `scripts/generate_cue_audio.py` reproduce them.
