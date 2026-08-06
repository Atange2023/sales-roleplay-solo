# DLC and stage progression

## Rules

Every purchased/installed DLC is independently selectable. The first stage inside each DLC is unlocked by default. Later stages require the immediately previous stage to be completed.

Passing learner outcomes are `stage_clear` and `professional_exit`. `needs_practice` and `game_over` never unlock the next stage. Completed stages remain replayable and can be jumped to on later launches.

## Commands

```text
py scripts/game_menu.py dlcs
py scripts/game_menu.py stages DLC01
py scripts/game_menu.py select DLC01 L02
py scripts/progress.py status --dlc DLC01 --stage L02
py scripts/progress.py record --dlc DLC01 --stage L01 --outcome stage_clear
```

The default file is `data/progress.json`. It is local UTF-8 JSON, written atomically, and preserved by updates. Never edit or replace a malformed progress file; surface the error for recovery.
