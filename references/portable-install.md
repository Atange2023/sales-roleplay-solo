# Portable offline install

The offline ZIP contains one top-level folder, `sales-roleplay-solo/`. Copy it into the skills directory of a Skill-capable Agent, restart or re-index that Agent, then start practice in the Agent chat. Do not run `roleplay.py` to practise: Python never replaces the host model.

Typical locations:

- Codex: `%USERPROFILE%\.codex\skills\sales-roleplay-solo`
- Reasonix: `.reasonix\skills\sales-roleplay-solo`
- OpenClaw/ArkClaw: `~/.openclaw/workspace/skills/sales-roleplay-solo`

Git install after a v0.4.2 tag exists:

```powershell
git clone --branch v0.4.2 --depth 1 https://github.com/Atange2023/sales-roleplay-solo.git "$env:USERPROFILE\.codex\skills\sales-roleplay-solo"
```

Offline self-check from the installed Skill folder:

```powershell
py scripts/roleplay.py --smoke --offline --no-audio
```

Text practice, fixed MP3, cues, progress, logs, CSV, and HTML require no network. Speech transcription and dynamic TTS depend on host capability.
