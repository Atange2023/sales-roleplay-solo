# Local logs and weekly reports

At finish, build a record through `scripts/session_engine.py` and append it to `data/sessions.jsonl`. Keep `data/` local and never upload it automatically.

Store the existing fields plus:

- difficulty, effective turns, high/medium/low counts, longest streaks;
- impulse and low-mood trigger counts, timeout, input modes, outcomes, red lines;
- DLC02-L01 evidence completeness and profile accuracy when applicable;
- DLC02-L02 policy-negotiation dimensions and total when applicable.

The additive v1.1 schema remains readable alongside older v1.0 records.

Export a leadership-readable seven-day HTML and CSV report with:

```powershell
py scripts/report.py --log data/sessions.jsonl --output-dir reports
```

The report includes practice frequency, stages, difficulty, duration, effective turns, scores, outcomes, and trend. It is a coaching report, not a formal examination record.
