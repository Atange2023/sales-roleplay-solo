# -*- coding: utf-8 -*-
"""Render the tutorial and validate the two-level DLC then stage menu."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from progress import DEFAULT_PATH, load_config, load_progress, stage_status

TUTORIAL = """HOW TO PLAY // 销售陪练
- 你扮演销售；宿主 Agent 扮演客户和教练。
- 游戏目标：通过提问理解客户，而不是强行成交。
- 教学模式下，每轮客户回应后都有教练分析和改良示例。
- 客户拒绝不等于失败；尊重边界可以专业退出并通关。
- 逼单、欺骗、无视明确拒绝或不当承诺会触发失败。
- 文字或语音转写可以随时混用，不会重置关卡。
- 随时说“暂停”“继续”或“结束并复盘”。"""


def render_dlc_menu(config: dict) -> str:
    lines = ["SELECT DLC"]
    lines.extend(f"{dlc['id']} [AVAILABLE] {dlc['name']}" for dlc in config["dlcs"])
    return "\n".join(lines)


def render_stage_menu(config: dict, progress: dict, dlc_id: str) -> str:
    dlc = next((item for item in config["dlcs"] if item["id"] == dlc_id), None)
    if dlc is None:
        raise ValueError(f"unknown DLC: {dlc_id}")
    lines = [f"SELECT STAGE // {dlc_id} {dlc['name']}"]
    for stage in dlc["stages"]:
        status = stage_status(config, progress, dlc_id, stage["id"]).upper()
        lines.append(f"{stage['id']} [{status}] {stage['name']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("tutorial")
    sub.add_parser("dlcs")
    stages = sub.add_parser("stages")
    stages.add_argument("dlc")
    stages.add_argument("--progress", type=Path, default=DEFAULT_PATH)
    select = sub.add_parser("select")
    select.add_argument("dlc")
    select.add_argument("stage")
    select.add_argument("--progress", type=Path, default=DEFAULT_PATH)
    args = parser.parse_args(argv)
    config = load_config()
    try:
        if args.command == "tutorial":
            print(TUTORIAL)
        elif args.command == "dlcs":
            print(render_dlc_menu(config))
        elif args.command == "stages":
            print(render_stage_menu(config, load_progress(args.progress), args.dlc))
        else:
            status = stage_status(config, load_progress(args.progress), args.dlc, args.stage)
            if status == "locked":
                print(f"LOCKED {args.dlc}-{args.stage}: pass the previous stage first")
                return 2
            print(f"SELECTED {args.dlc}-{args.stage} [{status.upper()}]")
    except ValueError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
