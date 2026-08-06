# Updating the Skill

Treat `sales-roleplay update` as an Agent intent, not a global operating-system command. The Agent resolves the installed Skill and runs its packaged updater.

```powershell
py scripts/update_skill.py check
py scripts/update_skill.py update
py scripts/update_skill.py rollback
```

The updater accepts an optional exact tag after `update`. It fetches only releases from `Atange2023/sales-roleplay-solo`, requires the offline ZIP plus `SHA256SUMS.txt`, verifies SHA-256 before changes, and creates a rollback backup. It preserves `.git/`, `data/`, `reports/`, including `data/progress.json`. Git installs stop on tracked local changes and update only by fast-forward.
