# -*- coding: utf-8 -*-
"""DOS/MUD-style offline-first sales roleplay launcher."""

from __future__ import annotations

import argparse
import sys
import time
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from report import export_weekly
from session_engine import DIMENSIONS, append_session, build_session
from speech_input import read_turn
from tts_speak import play_by_id

BANNER = r"""
+=====================================================+
|         SALES ROLEPLAY SOLO v0.4 // OFFLINE         |
|        CONSULTATIVE SALES TRAINING TERMINAL         |
+=====================================================+
"""

STAGES = {
    "1": ("manufacturing", {"1": ("L01", "张总单人拜访", "V1_standard"), "2": ("L02", "三人方案会", "B0_open")}),
    "2": ("business-school", {"1": ("L01", "商学院招生咨询", "B0_open_zhous")}),
}
DEFAULT_SCORES = {
    "intent_permission": 3,
    "listening": 3,
    "specificity": 2,
    "causal_inquiry": 2,
    "four_stage_diagnosis": 2,
    "solution_fit": 2,
    "decision_next_step": 3,
    "ethics_aftercare": 3,
}


def play_cue(name: str, no_audio: bool) -> None:
    path = ROOT / "assets" / "midi" / f"{name}.mid"
    print(f"[MIDI] {path.relative_to(ROOT).as_posix()}")
    if no_audio:
        return
    try:
        import winsound
        winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception:
        pass


def smoke(log: Path, report_dir: Path, no_audio: bool) -> int:
    print(BANNER)
    play_cue("boot", no_audio)
    print("[DLC] manufacturing  [STAGE] L01")
    print("[CUSTOMER] 我们现在不考虑推进了，谢谢。")
    record = build_session(
        dlc="manufacturing",
        stage="L01",
        duration_seconds=90,
        dimension_scores=DEFAULT_SCORES,
        customer_outcome="refused",
        red_lines=[],
        professional_exit=True,
        input_modes=("text", "voice"),
        notes="offline smoke flow",
    )
    append_session(log, record)
    play_cue(record["cue"], no_audio)
    print(f"[PROFESSIONAL EXIT] capability={record['capability']['total']}/24 customer=refused")
    export_weekly(log, report_dir, end_date=date.today())
    print(f"[REPORT] {report_dir / 'weekly-report.html'}")
    return 0


def choose_stage() -> tuple[str, str, str]:
    print("SELECT DLC: [1] 制造业  [2] 商学院")
    dlc_key = input("> ").strip()
    if dlc_key not in STAGES:
        raise ValueError("无效 DLC")
    dlc, stages = STAGES[dlc_key]
    print("SELECT STAGE:")
    for key, (_, label, _) in stages.items():
        print(f"[{key}] {label}")
    stage_key = input("> ").strip()
    if stage_key not in stages:
        raise ValueError("无效关卡")
    stage, _, opening = stages[stage_key]
    return dlc, stage, opening


def interactive(args) -> int:
    print(BANNER)
    play_cue("boot", args.no_audio)
    dlc, stage, opening = choose_stage()
    start = time.monotonic()
    mode = args.input_mode
    used_modes = [mode]
    audio = play_by_id(opening, launch=not args.no_audio, offline=args.offline)
    if audio:
        print(f"[CUSTOMER AUDIO] {audio[0]} -> {audio[1]}")
    print("输入 /voice 或 /text 可随时切换；/finish 结束并评分。")
    turns = 0
    while turns < 20:
        value = read_turn(mode)
        if value == "/voice":
            mode = "voice"
            used_modes.append(mode)
            continue
        if value == "/text":
            mode = "text"
            used_modes.append(mode)
            continue
        if value == "/finish":
            break
        turns += 1
        print("[CUSTOMER] 我听到了。请继续用问题澄清，而不是急着给方案。")
        play_by_id("B1_generic", launch=not args.no_audio, offline=args.offline)

    print("客户结果: advanced / delayed / refused / mismatch / referred")
    customer_outcome = input("> ").strip() or "delayed"
    print("是否完成专业退出? y/N")
    professional_exit = input("> ").strip().lower() == "y"
    scores = {}
    for name in DIMENSIONS:
        scores[name] = int(input(f"{name} [0-3]: ").strip())
    print("红线（无则回车，多个用逗号）:")
    red_lines = [x.strip() for x in input("> ").split(",") if x.strip()]
    record = build_session(
        dlc=dlc,
        stage=stage,
        duration_seconds=int(time.monotonic() - start),
        dimension_scores=scores,
        customer_outcome=customer_outcome,
        red_lines=red_lines,
        professional_exit=professional_exit,
        input_modes=used_modes,
    )
    append_session(args.log, record)
    play_cue(record["cue"], args.no_audio)
    export_weekly(args.log, args.report_dir)
    print(f"[{record['learner_outcome'].upper()}] {record['capability']['total']}/24 | customer={customer_outcome}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--no-audio", action="store_true")
    parser.add_argument("--input-mode", choices=("text", "voice"), default="text")
    parser.add_argument("--log", type=Path, default=ROOT / "data" / "sessions.jsonl")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    args = parser.parse_args(argv)
    if args.smoke:
        return smoke(args.log, args.report_dir, args.no_audio)
    return interactive(args)


if __name__ == "__main__":
    raise SystemExit(main())