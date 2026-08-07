# Portable offline install

The offline ZIP contains one top-level folder, `sales-roleplay-solo/`. Copy it into the skills directory of a Skill-capable Agent, restart or re-index that Agent, then start practice in the Agent chat. Do not run `roleplay.py` to practise: Python never replaces the host model.

Typical locations:

- Codex: `%USERPROFILE%\.codex\skills\sales-roleplay-solo`
- Reasonix: `.reasonix\skills\sales-roleplay-solo`
- OpenClaw/ArkClaw: `~/.openclaw/workspace/skills/sales-roleplay-solo`

Git installation follows the repository's currently published main branch:

```powershell
git clone https://github.com/Atange2023/sales-roleplay-solo.git "$env:USERPROFILE\.codex\skills\sales-roleplay-solo"
```

After installation, start from the Agent chat by saying “启动销售陪练”. The support-only offline self-check is:

```powershell
py scripts/roleplay.py --smoke --offline --no-audio
```

Text practice, packaged MP3, cues, progress, logs, CSV, and HTML require no network. Microphone transcription and non-fixed generated voice depend on host capability.
