---
name: sales-roleplay-solo
description: Use when a user wants to start, practise, continue, assess, or review a Chinese consultative-sales roleplay, or manage its stages, progress, reports, installation, update, or rollback.
---

# Sales Roleplay Solo v0.4.3

Conduct the intelligent roleplay in the current chat. The host Agent is the live customer and coach. Python supports media, menus, rules, state, progress, logs, reports, updates, and tests; never use it as a canned dialogue engine.

## Start in this order

1. Execute `py scripts/media_player.py cue boot` (`python3` on non-Windows). Claim sound only when the result says `"ok": true`.
2. Execute `py scripts/game_menu.py title`, then `py scripts/game_menu.py tutorial`.
3. Execute `py scripts/game_menu.py dlcs` and ask only for the numbered DLC choice.
4. After the DLC choice, execute `py scripts/game_menu.py stages <DLC_ID>` and ask for the numbered stage. Accept `1`, `1 简单`, or `1 困难`; default to `正常`.
5. Execute `py scripts/game_menu.py select <DLC_ID> <STAGE_ID> --difficulty <难度>`. A valid selection starts loading immediately. Never ask for another “开始第一关”.
6. Read [gameplay.md](references/gameplay.md), [agent-runtime.md](references/agent-runtime.md), [progression.md](references/progression.md), and [coaching-and-review.md](references/coaching-and-review.md). For DLC02 also read [dlc02-stage1.md](references/dlc02-stage1.md) or [dlc02-stage2.md](references/dlc02-stage2.md).
7. Load the selected scenario, persona, methods, and fixed-line assets, then let the customer open automatically.

Use Chinese game language for all player-visible status. Never expose model reasoning, scripts, TTS, MP3, JSON, manifests, branches, or fallback internals.

## Run every learner turn

1. Keep one session across typed text and microphone transcripts. Show:

   ```text
   【输入方式】直接输入文字，或点击麦克风说话
   【语音指令】输入 /voice 可启用本机录音
   ```

2. Treat `查看任务`, `查看规则`, `查看权限`, `暂停`, `继续`, `结束并复盘`, `/voice`, and `/text` as commands that consume no effective turn.
3. For a learner response, update discovered evidence, permission, boundaries, persona state, input modes, turn quality, streaks, and the effective-turn count.
4. Generate a customer reply specific to the conversation and hidden persona. Never answer with a generic “我听到了，请继续澄清”. Never reveal hidden truth before earned disclosure.
5. Prefer an unused fitting fixed line and actually execute `py scripts/tts_speak.py --play <ID> --offline`. If a matching fixed line does not exist, use the host's available voice. Say `【语音】客户正在组织语言……`; on voice failure say only `【提示】本轮语音暂不可用，已自动切换为文字，不影响关卡进度。`
6. Display the customer reply, then in default teaching mode add a parenthetical coach block with judgment, strength, improvement, better wording, evidence gained, and visible stage progress. Preserve the full v0.3 review depth.
7. Apply the difficulty and 20-turn rules in [gameplay.md](references/gameplay.md). Warn at effective turns 15 and 18. Turn 20 must resolve.

Switch to immersive mode only when explicitly requested. Restore coaching on pause, checkpoints, and finish.

## Finish and persist

- Keep learner capability, customer decision, policy compliance, and stage progression independent.
- For DLC02-L01, always collect the learner's eight persona estimates before revealing truth, even after failure; then report evidence completeness and profile accuracy.
- For DLC02-L02, report the additional policy-negotiation score and any authority or policy boundary.
- Follow the stage-specific outcome and unlock rules in [progression.md](references/progression.md). In DLC02-L01, only a qualified `stage_clear` unlocks L02; `professional_exit` records a professional close but does not unlock it.
- Build and append the session through `scripts/session_engine.py`, then record progression with `scripts/progress.py`.
- Use [review_template_v043.md](docs/review_template_v043.md), [review_template_v042.md](docs/review_template_v042.md), [review_template.md](docs/review_template.md), and both v0.3 examples for the full review.

For scoring, assets, logs/reports, installation, or updates, read [scoring.md](references/scoring.md), [audio-assets.md](references/audio-assets.md), [logs-and-reporting.md](references/logs-and-reporting.md), [portable-install.md](references/portable-install.md), or [updating.md](references/updating.md) as needed.
