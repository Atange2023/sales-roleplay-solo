# Gameplay flow

## Startup

Run the boot cue, tutorial, DLC menu, then the selected DLC's stage menu. Never collapse DLC and stage selection into one list.

The tutorial explains roles, question-first objective, per-turn coaching, professional exit, red lines, text/voice continuity, and pause/finish controls. Show it in full on first use; a returning learner may explicitly skip it.

## Stage play

- Manufacturing DLC01-L01: Zhang single visit, 15–20 turns.
- Manufacturing DLC01-L02: Zhang, Lao Zhao, and Lao Wang solution meeting, 20–25 turns; locked until DLC01-L01 passes.
- Business school DLC02-L01: Zhou, Lin, or Chen recruitment consultation, 15–18 turns; independently unlocked from first use.

Use v0.3 scenario scripts as the authoritative branch and pacing source. Rotate variants. Preserve checkpoint coaching in addition to the new teaching-mode feedback after every turn.

Recognize “暂停”, “继续”, “沉浸模式”, “教学模式”, and “结束并复盘”. Pausing preserves state. Finishing triggers the full review, media cue, session/progress write, and report offer.

## Outcomes and cues

- `stage_clear` → play `stage-clear`; unlock next stage.
- `professional_exit` → play `professional-exit`; unlock next stage.
- `needs_practice` → no unlock; offer same-stage retry.
- `game_over` → play `game-over`; no unlock; identify the verified red line.
- perfect 24/24 → play `achievement` after the normal outcome.

Customer `refused` may pair with learner `professional_exit`. Customer `advanced` may pair with learner `game_over` if pressure or deception caused it.
