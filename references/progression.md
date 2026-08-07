# DLC and stage progression

## Rules

Every installed DLC is independently selectable. Its first stage is unlocked by default. Later stages require completion of the immediately previous stage. Completed stages remain replayable.

Unlocking is stage-specific:

- DLC01 keeps the v0.4.2 contract: `stage_clear` and `professional_exit` complete the current stage.
- DLC02-L01 requires a qualified `stage_clear`: a permitted next action with counterpart, purpose, time window, explicit customer consent, and contact permission.
- DLC02-L01 `professional_exit` records a professional close and can earn strong capability scores, but it does not unlock L02.
- DLC02-L01 nurture, weak motivation, information shortage, free-benefit seeking, total failure, and timeout do not unlock L02.
- DLC02-L02 passes through normal registration, formal scholarship application, formal aid application, or valid special-condition approval.

Never infer completion from capability score alone. Customer result, learner capability, policy compliance, and progression are separate.

## Commands

```text
py scripts/game_menu.py dlcs
py scripts/game_menu.py stages DLC02
py scripts/game_menu.py select DLC02 L01 --difficulty 正常
py scripts/progress.py status --dlc DLC02 --stage L02
py scripts/progress.py record --dlc DLC02 --stage L01 --outcome stage_clear
```

The default file is `data/progress.json`. It is local UTF-8 JSON, written atomically, and preserved by updates. Never replace a malformed progress file; surface the error for recovery.
