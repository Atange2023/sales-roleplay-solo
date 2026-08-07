# -*- coding: utf-8 -*-
"""Render the Chinese DOS/MUD shell and validate DLC/stage navigation."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from progress import DEFAULT_PATH, default_progress, load_config, load_progress, stage_status

INPUT_HELP = "【输入方式】直接输入文字，或点击麦克风说话\n【语音指令】输入 /voice 可启用本机录音"

TUTORIAL = """【玩法介绍】
- 你扮演销售；在商学院关卡中，你扮演招生老师。
- 宿主 Agent 扮演客户和教练，通过真实对话与你练习。
- 游戏目标：通过提问理解客户，推进合格的下一步，而不是强行成交。
- 每轮客户回应后都会显示教练分析、改良建议和参考表达。
- 每局最多 20 个有效回合；请在了解情况后及时推进下一步。
- 客户拒绝不等于失败；识别边界并专业收场（专业退出）同样体现专业能力。
- 文字或语音可以随时混用，不会重置关卡。
- 可输入“暂停”“继续”“查看任务”或“结束并复盘”。"""

STATUS_LABELS = {"unlocked": "已解锁", "locked": "未解锁", "completed": "已完成"}


def render_title() -> str:
    return r"""
╔══════════════════════════════════════════════════════╗
║              SALES ROLEPLAY SOLO                    ║
║              销售实战模拟训练系统                   ║
║                    版本 0.4.3                       ║
╚══════════════════════════════════════════════════════╝
""".strip("\n")


def render_dlc_menu(config: dict) -> str:
    lines = ["【请选择训练内容】"]
    lines.extend(f"【{index}】{dlc['name']}" for index, dlc in enumerate(config["dlcs"], 1))
    lines.extend(("", "输入对应数字进入关卡选择。", INPUT_HELP))
    return "\n".join(lines)


def _dlc(config: dict, dlc_id: str) -> dict:
    dlc = next((item for item in config["dlcs"] if item["id"] == dlc_id), None)
    if dlc is None:
        raise ValueError(f"未知训练内容：{dlc_id}")
    return dlc


def render_stage_menu(config: dict, progress: dict, dlc_id: str) -> str:
    dlc = _dlc(config, dlc_id)
    lines = [f"【选择关卡】{dlc['name']}"]
    for index, stage in enumerate(dlc["stages"], 1):
        status = stage_status(config, progress, dlc_id, stage["id"])
        label = STATUS_LABELS[status]
        lines.extend((
            f"【{index}】{stage['name']}　【{label}】",
            "    默认难度：正常",
            f"    输入 {index} 开始；也可以输入：{index} 简单｜{index} 困难",
        ))
    lines.extend(("", INPUT_HELP))
    return "\n".join(lines)


def resolve_dlc_choice(config: dict, choice: str) -> str:
    value = choice.strip().upper()
    if value.isdigit():
        index = int(value) - 1
        if 0 <= index < len(config["dlcs"]):
            return config["dlcs"][index]["id"]
    for dlc in config["dlcs"]:
        if value == dlc["id"].upper():
            return dlc["id"]
    raise ValueError(f"无效训练内容：{choice}")


def parse_stage_choice(config: dict, dlc_id: str, choice: str) -> tuple[str, str]:
    dlc = _dlc(config, dlc_id)
    match = re.fullmatch(r"\s*(\S+)(?:\s+(\S+))?\s*", choice)
    if not match:
        raise ValueError("请输入关卡数字，可在数字后加简单或困难")
    stage_token, difficulty = match.group(1).upper(), match.group(2) or "正常"
    allowed = config.get("session_rules", {}).get("difficulties", ["简单", "正常", "困难"])
    if difficulty not in allowed:
        raise ValueError(f"未知难度：{difficulty}")
    if stage_token.isdigit():
        index = int(stage_token) - 1
        if 0 <= index < len(dlc["stages"]):
            return dlc["stages"][index]["id"], difficulty
    for stage in dlc["stages"]:
        if stage_token == stage["id"].upper():
            return stage["id"], difficulty
    raise ValueError(f"无效关卡：{stage_token}")


def render_loading_card(dlc_id: str, stage_id: str, difficulty: str, config: dict | None = None) -> str:
    config = config or load_config()
    dlc = _dlc(config, dlc_id)
    stage = next((item for item in dlc["stages"] if item["id"] == stage_id), None)
    if stage is None:
        raise ValueError(f"未知关卡：{dlc_id}-{stage_id}")
    return "\n".join((
        "关卡数据载入中……已就绪",
        "教练分析数据载入中……已就绪",
        f"【关卡】{stage['name']}",
        f"【难度：{difficulty}】",
        INPUT_HELP,
    ))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("title")
    sub.add_parser("tutorial")
    sub.add_parser("dlcs")
    stages = sub.add_parser("stages")
    stages.add_argument("dlc")
    stages.add_argument("--progress", type=Path, default=DEFAULT_PATH)
    select = sub.add_parser("select")
    select.add_argument("dlc")
    select.add_argument("stage")
    select.add_argument("--difficulty", default="正常")
    select.add_argument("--progress", type=Path, default=DEFAULT_PATH)
    args = parser.parse_args(argv)
    config = load_config()
    try:
        if args.command == "title":
            print(render_title())
        elif args.command == "tutorial":
            print(TUTORIAL)
        elif args.command == "dlcs":
            print(render_dlc_menu(config))
        elif args.command == "stages":
            print(render_stage_menu(config, load_progress(args.progress), resolve_dlc_choice(config, args.dlc)))
        else:
            dlc_id = resolve_dlc_choice(config, args.dlc)
            stage_id, parsed_difficulty = parse_stage_choice(config, dlc_id, f"{args.stage} {args.difficulty}".strip())
            status = stage_status(config, load_progress(args.progress), dlc_id, stage_id)
            if status == "locked":
                print(f"【未解锁】请先通过上一关：{dlc_id}-{stage_id}")
                return 2
            print(render_loading_card(dlc_id, stage_id, parsed_difficulty, config))
    except ValueError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
