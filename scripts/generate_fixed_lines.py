# -*- coding: utf-8 -*-
"""Generate the UTF-8 catalog for the 24 packaged fixed voice lines."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SYSTEM_LINES = (
    ("SYS_BOOT", "系统启动。请选择训练 DLC 和关卡。", "销售陪练已启动，请选择训练主题。", "coach_sys_boot_1.mp3"),
    ("SYS_STAGE_CLEAR", "关卡通过。", "关卡通过，你完成了本轮训练目标。", "coach_sys_stage_clear_1.mp3"),
    ("SYS_PROFESSIONAL_EXIT", "专业退出，边界识别正确。", "专业退出。你尊重了客户边界，本轮训练通过。", "coach_sys_professional_exit_1.mp3"),
    ("SYS_GAME_OVER", "本轮未通过。", "本轮出现关键失误，请复盘后再次挑战。", "coach_sys_game_over_1.mp3"),
    ("SYS_ACHIEVEMENT", "成就解锁。", "成就解锁，八项能力全部达到满分。", "coach_sys_achievement_1.mp3"),
)

ROLES = {
    "zhang": "张总",
    "laozhao": "赵总",
    "laowang": "王总",
    "zhous": "周总",
    "lin": "林主任",
    "chen": "陈老师",
}


def entry(line_id: str, role: str, role_name: str, scenario: str, display: str, spoken: str, filename: str) -> dict:
    return {
        "id": line_id,
        "variant": 1,
        "role": role,
        "role_name": role_name,
        "scenario": scenario,
        "display_text": display,
        "spoken_text": spoken,
        "file": f"assets/audio/fixed/{filename}",
        "fixed": True,
        "source": "v0.4-windows-sapi-pre-generated",
        "generation": {"engine": "Windows SAPI", "voice": "Microsoft Huihui Desktop", "rate": 0},
    }


def build() -> list[dict]:
    entries = [entry(line_id, "coach", "系统教练", "system", display, spoken, filename) for line_id, display, spoken, filename in SYSTEM_LINES]
    for role, name in ROLES.items():
        entries.extend((
            entry("ROLE_STAGE_CLEAR", role, name, "fixed-ending", f"{name}接受了本轮推进。", "好，我们可以进入下一步。", f"{role}_role_stage_clear_1.mp3"),
            entry("ROLE_PROFESSIONAL_EXIT", role, name, "fixed-ending", f"{name}明确暂不继续。", "谢谢理解，等有需要我再联系你。", f"{role}_role_professional_exit_1.mp3"),
            entry("ROLE_GAME_OVER", role, name, "fixed-ending", f"{name}终止了本轮沟通。", "先到这里吧，这种沟通方式我不能接受。", f"{role}_role_game_over_1.mp3"),
        ))
    entries.append(entry("ROLE_PROFESSIONAL_EXIT", "coach", "教练", "fixed-ending", "教练确认专业退出。", "你识别了边界，并以专业方式结束沟通。", "coach_role_professional_exit_1.mp3"))
    return entries


def main() -> int:
    destination = ROOT / "assets" / "fixed-lines.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps({"schema_version": "1.0", "entries": build()}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"WROTE {len(build())} -> {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
