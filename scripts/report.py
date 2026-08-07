# -*- coding: utf-8 -*-
"""Export leadership-readable weekly HTML and CSV from local JSONL logs."""

from __future__ import annotations

import argparse
import csv
import html
import json
from datetime import date, datetime, timedelta
from pathlib import Path


def load_records(path: Path | str) -> list[dict]:
    source = Path(path)
    if not source.exists():
        return []
    return [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def _simulation(item: dict) -> dict:
    return item.get("simulation") or {
        "difficulty": "正常", "effective_turns": 0,
        "quality_counts": {"high": 0, "medium": 0, "low": 0},
        "mood_triggers": {"impulse": 0, "low_mood": 0}, "timeout": False,
    }


def _nested_total(item: dict, section: str, nested: str | None = None) -> str:
    value = item.get(section)
    if not isinstance(value, dict):
        return ""
    if nested:
        value = value.get(nested)
        if not isinstance(value, dict):
            return ""
    total = value.get("total")
    return "" if total is None else str(total)


def export_weekly(log_path: Path | str, output_dir: Path | str, *, end_date: date | None = None) -> dict[str, Path]:
    ending = end_date or date.today()
    beginning = ending - timedelta(days=6)
    records = [item for item in load_records(log_path) if beginning <= datetime.fromisoformat(item["ended_at"]).date() <= ending]
    records.sort(key=lambda item: item["ended_at"])
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    csv_path = output / "weekly-report.csv"
    html_path = output / "weekly-report.html"
    fields = [
        "ended_at", "dlc", "stage", "difficulty", "duration_seconds", "effective_turns",
        "high_quality_turns", "medium_quality_turns", "low_quality_turns",
        "impulse_triggers", "low_mood_triggers", "timeout", "capability_total",
        "evidence_completeness_percent", "profile_accuracy_total", "policy_negotiation_total",
        "customer_outcome", "learner_outcome", "input_modes", "red_lines",
    ]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in records:
            simulation = _simulation(item)
            counts = simulation.get("quality_counts", {})
            triggers = simulation.get("mood_triggers", {})
            reconstruction = item.get("profile_reconstruction") or {}
            writer.writerow({
                "ended_at": item["ended_at"], "dlc": item["dlc"], "stage": item["stage"],
                "difficulty": simulation.get("difficulty", "正常"),
                "duration_seconds": item["duration_seconds"],
                "effective_turns": simulation.get("effective_turns", 0),
                "high_quality_turns": counts.get("high", 0),
                "medium_quality_turns": counts.get("medium", 0),
                "low_quality_turns": counts.get("low", 0),
                "impulse_triggers": triggers.get("impulse", 0),
                "low_mood_triggers": triggers.get("low_mood", 0),
                "timeout": simulation.get("timeout", False),
                "capability_total": item["capability"]["total"],
                "evidence_completeness_percent": reconstruction.get("evidence_completeness_percent", ""),
                "profile_accuracy_total": _nested_total(item, "profile_reconstruction", "profile_accuracy"),
                "policy_negotiation_total": _nested_total(item, "policy_negotiation"),
                "customer_outcome": item["customer_outcome"], "learner_outcome": item["learner_outcome"],
                "input_modes": "|".join(item.get("input_modes", [])), "red_lines": "|".join(item.get("red_lines", [])),
            })
    totals = [item["capability"]["total"] for item in records]
    average = round(sum(totals) / len(totals), 1) if totals else 0
    trend = "→"
    if len(totals) >= 2:
        trend = "↑" if totals[-1] > totals[0] else "↓" if totals[-1] < totals[0] else "→"
    duration_minutes = round(sum(item["duration_seconds"] for item in records) / 60, 1)
    rows = "".join(
        "<tr>"
        f"<td>{html.escape(item['ended_at'][:10])}</td><td>{html.escape(item['dlc'])}</td>"
        f"<td>{html.escape(item['stage'])}</td><td>{html.escape(str(_simulation(item).get('difficulty', '正常')))}</td>"
        f"<td>{_simulation(item).get('effective_turns', 0)}</td><td>{item['duration_seconds'] // 60}</td>"
        f"<td>{item['capability']['total']}/24</td><td>{html.escape(item['customer_outcome'])}</td>"
        f"<td>{html.escape(item['learner_outcome'])}</td></tr>" for item in records
    ) or '<tr><td colspan="9">本周暂无训练记录</td></tr>'
    html_text = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>销售陪练训练周报</title><style>body{{font-family:Segoe UI,Microsoft YaHei,sans-serif;background:#f4f6f8;color:#17202a;margin:0;padding:32px}}main{{max-width:1080px;margin:auto}}.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0}}.card{{background:white;padding:18px;border-radius:10px}}.value{{font-size:28px;font-weight:700}}table{{width:100%;border-collapse:collapse;background:white}}th,td{{padding:10px;border-bottom:1px solid #e6e9ed;text-align:left}}th{{background:#17202a;color:white}}</style></head><body><main><h1>销售陪练训练周报</h1><div>{beginning.isoformat()} — {ending.isoformat()}</div><section class="cards"><div class="card"><div>练习频次</div><div class="value">{len(records)}</div></div><div class="card"><div>训练时长（分钟）</div><div class="value">{duration_minutes}</div></div><div class="card"><div>平均能力分</div><div class="value">{average}/24</div></div><div class="card"><div>分数趋势</div><div class="value">{trend}</div></div></section><table><thead><tr><th>日期</th><th>DLC</th><th>关卡</th><th>难度</th><th>有效回合</th><th>分钟</th><th>能力分</th><th>客户结果</th><th>学员结果</th></tr></thead><tbody>{rows}</tbody></table><p>本报告用于训练复盘，不是正式考试成绩。客户结果与学员能力分别记录。</p></main></body></html>"""
    html_path.write_text(html_text, encoding="utf-8")
    return {"html": html_path, "csv": csv_path}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--end-date", type=date.fromisoformat)
    args = parser.parse_args(argv)
    outputs = export_weekly(args.log, args.output_dir, end_date=args.end_date)
    print(outputs["html"])
    print(outputs["csv"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
