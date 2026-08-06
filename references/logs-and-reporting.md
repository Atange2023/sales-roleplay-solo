# Local logs and weekly reports

At finish, build a record with `scripts/session_engine.py` and append it to `data/sessions.jsonl`. Store duration, DLC, stage, input modes, all eight scores, learner outcome, customer outcome, red lines, and notes. Keep `data/` local and never upload it automatically.

Export a leadership-readable seven-day report with:

```powershell
py scripts/report.py --log data/sessions.jsonl --output-dir reports
```

The command writes UTF-8 HTML and CSV showing practice frequency, stages, duration, scores, outcomes, and trend. The report is for coaching review, not a formal examination record.
