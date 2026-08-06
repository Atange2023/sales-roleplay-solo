# Portable offline install

The ZIP has one top-level folder named `sales-roleplay-solo`.

## Codex

1. Extract the ZIP.
2. Copy `sales-roleplay-solo` into the user's Codex `skills` directory.
3. Restart or open a new task so skills are re-indexed.
4. Run `py scripts/roleplay.py --smoke --offline --no-audio` from the Skill folder.

## Reasonix

Copy the same folder to the target workspace's `.reasonix\skills\sales-roleplay-solo` directory, restart Reasonix, and invoke the skill.

## Offline guarantees

No installation is required for text practice, packaged MP3 lookup, MIDI files, JSONL logs, CSV, or HTML reports. Python 3 is required for the included launchers. Audio playback uses an available local player; fixed MP3 files remain accessible even when automatic playback is unavailable.

Voice input uses Windows speech recognition when present. Dynamic TTS is optional and may require `edge-tts` plus network access; it is never required for fixed lines.