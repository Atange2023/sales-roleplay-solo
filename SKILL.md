---
name: sales-roleplay-solo
description: Use when a user wants to start, practise, continue, assess, or review a Chinese consultative-sales roleplay, or manage its stages, progress, reports, installation, update, or rollback.
---

# Sales Roleplay Solo v0.4.2

Conduct the live practice in the current chat. The host Agent is both the dynamic customer and the teaching coach; Python is support tooling only and must never become the dialogue engine.

## Start in this exact order

1. Actually execute `py scripts/media_player.py cue boot` (`python3` on non-Windows). Claim sound only when the result says `"ok": true`.
2. Execute `py scripts/game_menu.py tutorial` and show the short game introduction, goal, red lines, professional exit, input switching, pause, and finish controls.
3. Execute `py scripts/game_menu.py dlcs`. Ask for a DLC first; do not show a flat stage list.
4. Execute `py scripts/game_menu.py stages <DLC_ID>` only after selection. DLCs are independently available; locks apply only within a DLC.
5. Validate the stage through `py scripts/game_menu.py select <DLC_ID> <STAGE_ID>`. Never bypass a lock.

Before the first customer turn, read [gameplay.md](references/gameplay.md), [agent-runtime.md](references/agent-runtime.md), [progression.md](references/progression.md), and [coaching-and-review.md](references/coaching-and-review.md), then the selected scenario script, dialogue JSON, and relevant method references.

## Run every learner turn

1. Interpret typed text or the host's speech transcript as inputs to the same uninterrupted session.
2. Maintain the complete v0.3 scenario state, branches, D/T/O/P or multi-party support, red lines, and evidence.
3. Generate a customer response specific to the conversation. Never use a canned generic coaching reply as the customer.
4. Match a fixed line when available and actually run `py scripts/tts_speak.py --play <ID> --offline`. Report playback failure honestly and continue in text.
5. Display the customer response.
6. In default teaching mode, immediately show a parenthetical coach block containing: judgment, strength, improvement, better wording, and visible stage progress. Do not reveal hidden customer facts.

Switch to immersive mode only when explicitly requested; restore coaching on pause, checkpoints, and finish.

## Finish

Use [review_template_v042.md](docs/review_template_v042.md) for the current double-axis result and [review_template.md](docs/review_template.md) plus both v0.3 examples for full review depth. A clear customer refusal is not automatically learner failure. Respectful boundary recognition can be `professional_exit`; reserve `game_over` for real mistakes.

Record the outcome with `py scripts/progress.py record --dlc <DLC_ID> --stage <STAGE_ID> --outcome <learner_outcome>`. Only `stage_clear` and `professional_exit` unlock the next stage.

For scoring, assets, logs/reports, installation, or updates, read [scoring.md](references/scoring.md), [audio-assets.md](references/audio-assets.md), [logs-and-reporting.md](references/logs-and-reporting.md), [portable-install.md](references/portable-install.md), or [updating.md](references/updating.md) as needed.
