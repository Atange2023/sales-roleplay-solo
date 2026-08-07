# -*- coding: utf-8 -*-
"""Independent-DLC, sequential-stage progress storage."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "assets" / "game-config.json"
DEFAULT_PATH = ROOT / "data" / "progress.json"
PASSING_OUTCOMES = {"stage_clear", "professional_exit"}
OUTCOMES = PASSING_OUTCOMES | {"needs_practice", "game_over"}


def load_config(path: Path = CONFIG_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def default_progress() -> dict:
    return {"schema_version": "1.0", "dlcs": {}, "last_outcomes": {}}


def load_progress(path: Path | str = DEFAULT_PATH) -> dict:
    source = Path(path)
    if not source.exists():
        return default_progress()
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"malformed progress: {exc}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("dlcs"), dict):
        raise ValueError("malformed progress: dlcs must be an object")
    payload.setdefault("last_outcomes", {})
    return payload


def _dlc(config: dict, dlc_id: str) -> dict:
    for dlc in config["dlcs"]:
        if dlc["id"] == dlc_id:
            return dlc
    raise ValueError(f"unknown DLC: {dlc_id}")


def _stage(config: dict, dlc_id: str, stage_id: str) -> dict:
    for stage in _dlc(config, dlc_id)["stages"]:
        if stage["id"] == stage_id:
            return stage
    raise ValueError(f"unknown stage: {dlc_id}-{stage_id}")


def stage_status(config: dict, progress: dict, dlc_id: str, stage_id: str) -> str:
    stages = _dlc(config, dlc_id)["stages"]
    ids = [stage["id"] for stage in stages]
    if stage_id not in ids:
        raise ValueError(f"unknown stage: {dlc_id}-{stage_id}")
    completed = set(progress.get("dlcs", {}).get(dlc_id, {}).get("completed", []))
    if stage_id in completed:
        return "completed"
    index = ids.index(stage_id)
    if index == 0 or ids[index - 1] in completed:
        return "unlocked"
    return "locked"


def save_progress(path: Path | str, progress: dict) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_text(json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(destination)
    return destination


def record_outcome(path: Path | str, dlc_id: str, stage_id: str, learner_outcome: str) -> dict:
    if learner_outcome not in OUTCOMES:
        raise ValueError(f"unknown learner outcome: {learner_outcome}")
    config = load_config()
    progress = load_progress(path)
    stage_status(config, progress, dlc_id, stage_id)
    completed = progress["dlcs"].setdefault(dlc_id, {}).setdefault("completed", [])
    stage_config = _stage(config, dlc_id, stage_id)
    unlock_outcomes = set(stage_config.get("unlock_outcomes", PASSING_OUTCOMES))
    if learner_outcome in unlock_outcomes and stage_id not in completed:
        completed.append(stage_id)
    progress["last_outcomes"][f"{dlc_id}-{stage_id}"] = learner_outcome
    save_progress(path, progress)
    return progress


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    status = sub.add_parser("status")
    record = sub.add_parser("record")
    for item in (status, record):
        item.add_argument("--path", type=Path, default=DEFAULT_PATH)
        item.add_argument("--dlc", required=True)
        item.add_argument("--stage", required=True)
    record.add_argument("--outcome", required=True, choices=sorted(OUTCOMES))
    args = parser.parse_args(argv)
    try:
        if args.command == "status":
            print(stage_status(load_config(), load_progress(args.path), args.dlc, args.stage))
        else:
            record_outcome(args.path, args.dlc, args.stage, args.outcome)
            print(f"RECORDED {args.dlc}-{args.stage} {args.outcome}")
    except ValueError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
