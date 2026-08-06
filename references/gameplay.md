# Gameplay

## Session flow

1. Show the DOS/MUD boot screen and play `assets/midi/boot.mid`.
2. Select one existing DLC:
   - Manufacturing L01: single visit with Zhang
   - Manufacturing L02: three-party solution meeting
   - Business school L01: recruitment consultation
3. State privacy and input-mode boundaries.
4. Start with a packaged role opening from `assets/audio-manifest.json`.
5. Alternate learner turns and spoken customer responses. The display text may be longer than the low-latency spoken line.
6. Accept `/voice` and `/text` at any turn. Voice uses local Windows recognition when available; failure returns to text.
7. Finish when the customer advances, delays, refuses, is not a match, is referred, or the learner commits a red-line error.
8. Score, log, play the matching MIDI cue, and offer the weekly report.

## Offline command

```powershell
py scripts/roleplay.py --offline
```

Use `--no-audio` for classrooms or automated validation. Text input remains fully usable for multiple learners in the same room.

## Fixed outcome cues

| Learner outcome | MIDI | Meaning |
| --- | --- | --- |
| `stage_clear` | `stage-clear.mid` | Capability threshold met |
| `professional_exit` | `professional-exit.mid` | Boundary recognized and respected |
| `game_over` | `game-over.mid` | A real red-line error occurred |
| perfect 24/24 | `achievement.mid` | All eight dimensions reached 3 |

A customer refusal may pair with `professional_exit`. A customer advancement may still pair with `game_over` when the learner used pressure or deception.