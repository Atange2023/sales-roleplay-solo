# -*- coding: utf-8 -*-
"""Build one UTF-8 audio catalog for all shipped dialogue assets."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def scenario_entries() -> list[dict]:
    databases = (
        (ROOT / "scenarios" / "zhang_dialogue.json", ROOT / "audio", False),
        (ROOT / "scenarios" / "three_party_dialogue.json", ROOT / "audio3", True),
        (ROOT / "scenarios" / "business_school_dialogue.json", ROOT / "audio4", True),
    )
    entries: list[dict] = []
    for database, audio_dir, multi_role in databases:
        data = json.loads(database.read_text(encoding="utf-8"))
        items = data["branches"] if multi_role else data["openings"] + data["branches"]
        for item in items:
            texts = item.get("replies") or [item["text"]]
            if multi_role:
                role = item["char"]
                actor = data["characters"][role]
                prefix = f"{role}_"
            else:
                role = "zhang"
                actor = data["persona"]
                prefix = ""
            for variant, spoken in enumerate(texts, 1):
                path = audio_dir / f"{prefix}{item['id']}_{variant}.mp3"
                entries.append({
                    "id": item["id"], "variant": variant, "role": role,
                    "role_name": actor.get("name", role),
                    "scenario": data.get("scene", "manufacturing-single"),
                    "display_text": spoken, "spoken_text": spoken,
                    "file": path.relative_to(ROOT).as_posix(), "fixed": True,
                    "source": "v0.3-pre-generated",
                    "generation": {"voice": actor.get("voice", "zh-CN-YunyangNeural"), "rate": actor.get("rate", "-8%")},
                })
    return entries


def fixed_entries() -> list[dict]:
    source = ROOT / "assets" / "fixed-lines.json"
    return json.loads(source.read_text(encoding="utf-8"))["entries"]


def build(destination: Path | None = None) -> Path:
    target = destination or ROOT / "assets" / "audio-manifest.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    legacy = scenario_entries()
    fixed = fixed_entries()
    payload = {
        "schema_version": "1.1",
        "legacy_entry_count": len(legacy),
        "fixed_v04_entry_count": len(fixed),
        "entries": legacy + fixed,
    }
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target


if __name__ == "__main__":
    output = build()
    print(f"WROTE -> {output}")
