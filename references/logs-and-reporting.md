# Logs and weekly reporting

Sessions are local UTF-8 JSON Lines with schema version 1.0. The default path is `data/sessions.jsonl`; users may override it with `--log`.

Each record contains timestamp, DLC, stage, duration, input modes, all eight dimension scores, total/max, customer outcome, learner outcome, professional-exit flag, red lines, cue, and optional notes.

Export the current seven-day window:

```powershell
py scripts/report.py --log data/sessions.jsonl --output-dir reports
```

Outputs:

- `weekly-report.html`: leadership-readable frequency, stages, duration, average score, trend, customer outcomes, and learner outcomes.
- `weekly-report.csv`: portable row-level data for analysis.

This is a training report, not a formal examination result. Delete the local JSONL and reports when the learner no longer wants them retained.