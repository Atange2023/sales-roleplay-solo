---
name: sales-roleplay-solo
description: Use when a user wants to practise, simulate, assess, or review a Chinese consultative-sales conversation with customer roleplay, spoken responses, objection handling, discovery questions, proposal timing, professional exit, or after-sales follow-up.
---

# Sales Roleplay Solo v0.4

Run an offline-first Chinese sales practice game. Keep learner capability separate from the customer's autonomous decision.

## Start

1. Read [gameplay.md](references/gameplay.md) before starting a session.
2. Run `py scripts/roleplay.py --offline` for the DOS/MUD launcher.
3. Let the learner switch between text and voice with `/text` and `/voice`. Keep text available whenever voice recognition is unavailable or disruptive.
4. Play packaged fixed audio for every customer/system response. Resolve a line with `py scripts/tts_speak.py --play <ID> --offline`; use dynamic TTS only as an explicitly online fallback.
5. End with one learner outcome and one independent customer outcome. Read [scoring.md](references/scoring.md) before scoring.
6. Append the session log and export HTML/CSV when requested. Read [logs-and-reporting.md](references/logs-and-reporting.md).

## Non-negotiable rules

- Treat a clear refusal as a boundary, not a puzzle. Stop advancing, thank the customer, and optionally ask permission to keep contact.
- Allow `professional_exit` to pass when the learner identifies the boundary and exits well.
- Use `game_over` only for real learner errors such as pressure after refusal, deception, ignoring material constraints, or unsafe promises.
- Score eight observable capabilities at 0–3 each (maximum 24). Never add customer advancement to the capability score.
- Keep fixed dialogue, MIDI, text practice, local logs, and reports usable without a network.
- Do not use real customer personal data, secrets, or regulated information.

## Load references as needed

- Read [audio-assets.md](references/audio-assets.md) for manifest fields, local-first lookup, generation provenance, and regeneration.
- Read [portable-install.md](references/portable-install.md) when copying or installing the offline package.
- Read [privacy-and-boundaries.md](references/privacy-and-boundaries.md) before enterprise workshops or voice input.
- Use `py scripts/report.py --help` and `py scripts/roleplay.py --help` for CLI options.