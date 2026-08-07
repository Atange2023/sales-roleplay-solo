# -*- coding: utf-8 -*-
"""Generate the UTF-8 catalog for packaged fixed voice lines."""

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

ROLES = {"zhang": "张总", "laozhao": "赵总", "laowang": "王总", "zhous": "周总", "lin": "林主任", "chen": "陈老师"}

L02_LINES = (
    ("L02_BOSS_OPEN", "boss", "企业老板", "价格我可以谈，但你得保证我以后任何时候不满意都能退。", "l02_boss_open_1.mp3"),
    ("L02_SCHOLAR_OPEN", "scholar", "高分学员", "以我的背景，先确认奖学金比例，我才交材料。", "l02_scholar_open_1.mp3"),
    ("L02_EMPLOYEE_OPEN", "employee", "职场学员", "硕博连读能不能先按优惠价交，然后我再退掉博士阶段？", "l02_employee_open_1.mp3"),
    ("L02_CORPORATE_OPEN", "corporate", "企业付费学员", "公司愿意出钱，但付款节点和发票内容要符合我们的审批。", "l02_corporate_open_1.mp3"),
    ("L02_RESOURCE_OPEN", "resource", "合作型企业家", "如果学校愿意组织学员参观我的公司并设一个校友活动点，我就报名缴费。", "l02_resource_open_1.mp3"),
    ("L02_NORMAL_PASS", "coach", "系统教练", "客户已确认按规定完成报名缴费流程，本关通过。", "l02_normal_pass_1.mp3"),
    ("L02_SCHOLARSHIP_PASS", "coach", "系统教练", "奖学金正式申请已按规定提交，本关通过。", "l02_scholarship_pass_1.mp3"),
    ("L02_AID_PASS", "coach", "系统教练", "助学金材料已提交正确权限人审核，本关通过。", "l02_aid_pass_1.mp3"),
    ("L02_SPECIAL_PASS", "coach", "系统教练", "特殊条件与客户承诺已经闭环，并提交校领导审批，本关通过。", "l02_special_pass_1.mp3"),
    ("L02_NONPASS", "coach", "系统教练", "客户尚未形成明确报名行动，本关未通关。", "l02_nonpass_1.mp3"),
    ("L02_TIMEOUT", "coach", "系统教练", "有效回合已经用完，客户态度仍未明确，本局结束。", "l02_timeout_1.mp3"),
    ("L02_POLICY_FAILURE", "coach", "系统教练", "本轮出现越权承诺或政策违规，本局失败。", "l02_policy_failure_1.mp3"),
)


def entry(line_id: str, role: str, role_name: str, scenario: str, display: str, spoken: str, filename: str, *, source: str = "v0.4-windows-sapi-pre-generated") -> dict:
    return {
        "id": line_id, "variant": 1, "role": role, "role_name": role_name,
        "scenario": scenario, "display_text": display, "spoken_text": spoken,
        "file": f"assets/audio/fixed/{filename}", "fixed": True, "source": source,
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
    entries.extend(
        entry(line_id, role, role_name, "dlc02-enrollment-negotiation", spoken, spoken, filename, source="v0.4.3-windows-sapi-pre-generated")
        for line_id, role, role_name, spoken, filename in L02_LINES
    )
    return entries


def main() -> int:
    destination = ROOT / "assets" / "fixed-lines.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps({"schema_version": "1.1", "entries": build()}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"WROTE {len(build())} -> {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
