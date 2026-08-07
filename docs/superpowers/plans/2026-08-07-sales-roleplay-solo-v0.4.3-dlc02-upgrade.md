# Sales Roleplay Solo v0.4.3 DLC02 Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to execute this plan task by task. Apply superpowers:test-driven-development to every behavior change and superpowers:writing-skills when changing the Skill instructions.

**Goal:** Deliver v0.4.3 with a Chinese DOS/MUD game shell, a redesigned DLC02 first stage, a new policy-negotiation second stage, deterministic turn/difficulty/outcome rules, preserved v0.4.2 capabilities, and a portable offline Skill package.

**Architecture:** Keep the host Agent as customer and coach. Python modules provide deterministic menu, progression, state, scoring, asset, log, and report services; JSON files provide versioned game content and policies. The Skill instructions coordinate these services without replacing the host model's semantic conversation.

**Tech Stack:** Python 3 standard library, JSON/JSONL, HTML/CSV reports, local MP3/MIDI/WAV assets, unittest, Agent Skill Markdown/YAML.

## Global Constraints

- Work only on `codex/v0.4.3-dlc02-upgrade` in the isolated worktree.
- Preserve user data and exclude `data/`, caches, and temporary test output from commits.
- Preserve all v0.3/v0.4.2 accepted behavior and all 145 legacy MP3 files.
- Use RED → GREEN → REFACTOR for each production behavior.
- Do not publish, push, tag, or create a Release without separate authorization.

## Task 1: Lock version and content contracts

- [ ] Add failing asset/config tests for version `0.4.3`, DLC02-L02, three difficulties, 20-turn cap, persona data, school policy, and parseable nonempty manifests.
- [ ] Run the focused tests and confirm failures identify missing v0.4.3 contracts.
- [ ] Update `assets/version.json` and `assets/game-config.json`.
- [ ] Add `assets/dlc02-personas.json` with L01 truth profiles and L02 negotiation profiles.
- [ ] Add `assets/dlc02-school-policy.json` with rules, authority matrix, pass paths, and red lines.
- [ ] Re-run focused tests until green.

## Task 2: Build the Chinese DOS/MUD startup and navigation

- [ ] Add failing behavioral tests for the bilingual character title, Chinese tutorial, numbered DLC menu, Chinese stage states, direct stage start, difficulty parsing, loading messages, and persistent text/voice help.
- [ ] Confirm the old English menu fails the tests for the intended reasons.
- [ ] Update `scripts/game_menu.py` with `render_title`, Chinese menus, numeric selection resolution, and `parse_stage_choice`.
- [ ] Update `scripts/speech_input.py` only where needed to expose friendly Chinese help/fallback text.
- [ ] Preserve existing CLI entry points while adding new behavior.
- [ ] Re-run navigation, CLI, and speech tests until green.

## Task 3: Implement the deterministic 20-turn difficulty engine

- [ ] Add `tests/test_simulator_state.py` first for effective/non-effective turns, warnings at 15/18, mandatory resolution at 20, quality counts, easy three-high impulse, hard two-low depression, recovery/reset rules, and normal neutrality.
- [ ] Confirm import/API failures are the expected RED state.
- [ ] Add `scripts/simulator_state.py` with pure functions for session state and turn application.
- [ ] Ensure mood changes accelerate decisions but never alter policy or authority validation.
- [ ] Re-run focused tests and refactor only while green.

## Task 4: Implement DLC02-L01 diagnosis and reconstruction

- [ ] Add `tests/test_dlc02_stage1.py` first for 15 evidence fields, eight hidden truth dimensions, all ending categories, qualified-action requirements, professional-close non-unlock, and `/24` reconstruction comparison for every ending.
- [ ] Confirm failures demonstrate the rules module is absent/incomplete.
- [ ] Add `scripts/dlc02_rules.py` loaders, validators, `evaluate_l01_outcome`, and `score_profile_estimate`.
- [ ] Add stage-specific unlock outcomes to config and update `scripts/progress.py` so only a qualified L01 stage clear unlocks L02.
- [ ] Re-run focused plus legacy progress tests until green.

## Task 5: Implement DLC02-L02 policy negotiation

- [ ] Add `tests/test_dlc02_stage2.py` first for the four pass routes, conditional approval gates, authority routing, ordinary non-pass outcomes, professional close, timeout, and immediate severe-failure promises.
- [ ] Confirm each tested failure names a missing or wrong branch.
- [ ] Extend `scripts/dlc02_rules.py` with `evaluate_l02_outcome`, special-condition validation, red-line detection, and the second eight-dimension score validator.
- [ ] Add briefing/render helpers that expose background, policy, authority, and goal in Chinese without internal implementation language.
- [ ] Re-run focused tests until green.

## Task 6: Extend sessions, reports, and progress compatibility

- [ ] Add failing tests for difficulty, effective turns, quality counts, mood triggers, timeout, L01 reconstruction, L02 policy score, and preserved old call signatures.
- [ ] Extend `scripts/session_engine.py` schema additively; never discard v0.4.2 fields.
- [ ] Extend `scripts/report.py` CSV/HTML exports with the new fields and tolerant parsing of older logs.
- [ ] Verify upgrade/progress tests preserve existing completion and user logs.
- [ ] Run report and session tests until green.

## Task 7: Update Skill orchestration and fixed assets

- [ ] Define Agent behavior evaluation cases before editing instructions: startup flow, per-turn coaching, voice/text switching, L01 reconstruction, L02 briefing, no internal leakage, and turn-20 resolution.
- [ ] Update `SKILL.md` with a `Use when...` description and concise host-Agent workflow.
- [ ] Add `references/dlc02-stage1.md` and `references/dlc02-stage2.md`; update `references/gameplay.md`, `references/agent-runtime.md`, `references/progression.md`, `references/scoring.md`, and `references/logs-and-reporting.md` without duplicating detailed content.
- [ ] Update `agents/openai.yaml` to match v0.4.3.
- [ ] Add reusable fixed L02 opening/ending lines, generate actual offline audio with local Windows TTS, and update `assets/fixed-lines.json` plus `assets/audio-manifest.json`.
- [ ] Verify 145 legacy MP3 files remain nonempty and every new manifest entry resolves to a nonempty file.

## Task 8: Full verification and portable delivery

- [ ] Run every automated test from a clean command.
- [ ] Run skill-creator `quick_validate.py` on the Skill root.
- [ ] Execute a fresh-install startup smoke test, one L01 ending with profile comparison, one L02 pass, voice/text switching, turn-20 timeout, and actual HTML/CSV weekly report export.
- [ ] Build the offline ZIP with top-level `sales-roleplay-solo/` only.
- [ ] Generate `SHA256SUMS.txt` and `VALIDATION_REPORT.md` with observed counts and commands.
- [ ] Inspect Git status and stage only intended v0.4.3 files; leave `data/` and caches untouched.
- [ ] Use superpowers:verification-before-completion, then superpowers:finishing-a-development-branch for the local handoff. Do not push.
