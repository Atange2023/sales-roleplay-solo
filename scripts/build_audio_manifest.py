# -*- coding: utf-8 -*-
"""Build the unified fixed-line audio manifest."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from tts_speak import _scenario_entries


def build_manifest() -> dict:
    fixed = json.loads((ROOT / "assets" / "fixed-lines.json").read_text(encoding="utf-8"))["entries"]
    entries = _scenario_entries() + fixed
    entries.sort(key=lambda item: (item["scenario"], item["role"], item["id"], item["variant"]))
    return {
        "schema_version": "1.0",
        "generated_by": "scripts/build_audio_manifest.py",
        "legacy_entry_count": sum(item["source"] == "v0.3-pre-generated" for item in entries),
        "fixed_v04_entry_count": sum(item["source"] == "v0.4-windows-sapi-pre-generated" for item in entries),
        "entries": entries,
    }


def main() -> int:
    destination = ROOT / "assets" / "audio-manifest.json"
    destination.write_text(json.dumps(build_manifest(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())