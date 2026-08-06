# -*- coding: utf-8 -*-
"""Update Sales Roleplay Solo from signed GitHub Release metadata.

The updater keeps learner-owned ``data`` and ``reports`` directories in place.
Git clones advance by fast-forwarding to the release tag; portable ZIP installs
are backed up before verified release files are copied over them.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path


REPOSITORY = "Atange2023/sales-roleplay-solo"
API_ROOT = f"https://api.github.com/repos/{REPOSITORY}/releases"
PRESERVED_TOP_LEVEL = {".git", "data", "reports"}
BACKUP_ROOT_NAME = ".sales-roleplay-solo-backups"
BACKUP_METADATA = ".update-backup.json"


class UpdateError(RuntimeError):
    """Raised when an update cannot be verified or safely applied."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_version(root: Path) -> str:
    version_file = root / "assets" / "version.json"
    if not version_file.is_file():
        return "v0.4.0-or-earlier"
    try:
        value = json.loads(version_file.read_text(encoding="utf-8"))["version"]
    except (KeyError, json.JSONDecodeError, OSError) as exc:
        raise UpdateError(f"Invalid version metadata: {version_file}") from exc
    return str(value)


def select_release_assets(payload: dict) -> dict[str, str]:
    version = str(payload.get("tag_name", "")).strip()
    assets = payload.get("assets") or []
    zip_asset = next(
        (
            item
            for item in assets
            if str(item.get("name", "")).startswith("sales-roleplay-solo-")
            and str(item.get("name", "")).endswith("-offline.zip")
        ),
        None,
    )
    sha_asset = next((item for item in assets if item.get("name") == "SHA256SUMS.txt"), None)
    if not version or not zip_asset or not sha_asset:
        raise UpdateError("Release must contain a versioned offline ZIP and SHA256SUMS.txt")
    return {
        "version": version,
        "zip_name": str(zip_asset["name"]),
        "zip_url": str(zip_asset["browser_download_url"]),
        "sha_url": str(sha_asset["browser_download_url"]),
    }


def _request_bytes(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "sales-roleplay-solo-updater"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise UpdateError(f"Network request failed: {url}") from exc


def fetch_release(version: str | None = None) -> dict:
    url = f"{API_ROOT}/latest"
    if version:
        url = f"{API_ROOT}/tags/{urllib.parse.quote(version, safe='')}"
    try:
        return json.loads(_request_bytes(url).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise UpdateError("GitHub returned invalid release metadata") from exc


def parse_checksum(text: str, filename: str) -> str:
    for raw_line in text.splitlines():
        parts = raw_line.strip().split(maxsplit=1)
        if len(parts) != 2:
            continue
        digest, listed_name = parts
        if listed_name.lstrip("*").strip() == filename and len(digest) == 64:
            try:
                int(digest, 16)
            except ValueError:
                continue
            return digest.lower()
    raise UpdateError(f"No SHA-256 entry found for {filename}")


def _safe_extract(archive: Path, destination: Path) -> Path:
    with zipfile.ZipFile(archive) as handle:
        for member in handle.infolist():
            member_path = Path(member.filename.replace("\\", "/"))
            if member_path.is_absolute() or ".." in member_path.parts:
                raise UpdateError(f"Unsafe archive member: {member.filename}")
        handle.extractall(destination)
    skill_root = destination / "sales-roleplay-solo"
    if not (skill_root / "SKILL.md").is_file() or not (skill_root / "assets" / "version.json").is_file():
        raise UpdateError("Offline ZIP does not contain a valid sales-roleplay-solo Skill")
    return skill_root


def _relative_files(root: Path) -> list[str]:
    files = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if relative.parts and relative.parts[0] in PRESERVED_TOP_LEVEL:
            continue
        if relative.as_posix() == BACKUP_METADATA:
            continue
        files.append(relative.as_posix())
    return sorted(files)


def _copy_managed_tree(source: Path, destination: Path) -> None:
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        if not relative.parts or relative.parts[0] in PRESERVED_TOP_LEVEL:
            continue
        if relative.as_posix() == BACKUP_METADATA:
            continue
        target = destination / relative
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def _new_backup_dir(install_root: Path, version: str) -> Path:
    backup_root = install_root.parent / BACKUP_ROOT_NAME
    backup_root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_version = version.replace("/", "-").replace("\\", "-")
    candidate = backup_root / f"{stamp}-{safe_version}"
    counter = 1
    while candidate.exists():
        candidate = backup_root / f"{stamp}-{safe_version}-{counter}"
        counter += 1
    return candidate


def apply_archive(archive: Path | str, install_root: Path | str, *, expected_sha256: str) -> dict[str, str]:
    archive_path = Path(archive).resolve()
    root = Path(install_root).resolve()
    actual = sha256_file(archive_path)
    if actual.lower() != expected_sha256.lower():
        raise UpdateError(f"SHA-256 mismatch: expected {expected_sha256}, got {actual}")
    if not root.is_dir() or not (root / "SKILL.md").is_file():
        raise UpdateError(f"Skill installation not found: {root}")

    with tempfile.TemporaryDirectory(prefix="sales-roleplay-update-", dir=root.parent) as tmp:
        staged_root = _safe_extract(archive_path, Path(tmp))
        from_version = read_version(root)
        to_version = read_version(staged_root)
        backup = _new_backup_dir(root, from_version)
        backup.mkdir(parents=True)
        old_files = _relative_files(root)
        new_files = _relative_files(staged_root)
        _copy_managed_tree(root, backup)
        (backup / BACKUP_METADATA).write_text(
            json.dumps(
                {
                    "kind": "portable",
                    "from_version": from_version,
                    "to_version": to_version,
                    "old_files": old_files,
                    "installed_files": new_files,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        _copy_managed_tree(staged_root, root)

    return {
        "from_version": from_version,
        "to_version": to_version,
        "backup": str(backup),
        "sha256": actual,
    }


def _run_git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=120,
    )
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise UpdateError(f"Git command failed: {detail}")
    return completed.stdout.strip()


def update_git_install(root: Path, version: str) -> dict[str, str]:
    dirty = _run_git(root, "status", "--porcelain", "--untracked-files=no")
    if dirty:
        raise UpdateError("Tracked Skill files have local changes; update aborted without overwriting them")
    previous_commit = _run_git(root, "rev-parse", "HEAD")
    from_version = read_version(root)
    _run_git(root, "fetch", "--tags", "origin")
    target_commit = _run_git(root, "rev-list", "-n", "1", version)
    if not target_commit:
        raise UpdateError(f"Release tag not found: {version}")
    _run_git(root, "merge", "--ff-only", target_commit)
    backup = _new_backup_dir(root, from_version)
    backup.mkdir(parents=True)
    (backup / BACKUP_METADATA).write_text(
        json.dumps(
            {
                "kind": "git",
                "from_version": from_version,
                "to_version": version,
                "previous_commit": previous_commit,
                "installed_commit": target_commit,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return {"from_version": from_version, "to_version": version, "backup": str(backup)}


def _latest_backup(root: Path) -> Path:
    backup_root = root.parent / BACKUP_ROOT_NAME
    candidates = [path for path in backup_root.glob("*") if (path / BACKUP_METADATA).is_file()]
    if not candidates:
        raise UpdateError("No rollback backup is available")
    return max(candidates, key=lambda path: path.stat().st_mtime_ns)


def rollback_latest(install_root: Path | str) -> dict[str, str]:
    root = Path(install_root).resolve()
    backup = _latest_backup(root)
    metadata = json.loads((backup / BACKUP_METADATA).read_text(encoding="utf-8"))
    if metadata.get("kind") == "git":
        dirty = _run_git(root, "status", "--porcelain", "--untracked-files=no")
        if dirty:
            raise UpdateError("Tracked Skill files have local changes; rollback aborted")
        _run_git(root, "reset", "--hard", str(metadata["previous_commit"]))
    else:
        old_files = set(metadata.get("old_files", []))
        for relative in metadata.get("installed_files", []):
            if relative in old_files:
                continue
            target = root / relative
            if target.is_file():
                target.unlink()
        _copy_managed_tree(backup, root)
    return {"restored_version": str(metadata["from_version"]), "backup": str(backup)}


def update(install_root: Path, version: str | None = None) -> dict[str, str]:
    release = select_release_assets(fetch_release(version))
    current = read_version(install_root)
    if current == release["version"]:
        return {"from_version": current, "to_version": current, "status": "up-to-date"}
    if (install_root / ".git").exists():
        result = update_git_install(install_root, release["version"])
        result["status"] = "updated"
        return result

    with tempfile.TemporaryDirectory(prefix="sales-roleplay-download-", dir=install_root.parent) as tmp:
        archive = Path(tmp) / release["zip_name"]
        archive.write_bytes(_request_bytes(release["zip_url"]))
        sums = _request_bytes(release["sha_url"]).decode("utf-8")
        expected = parse_checksum(sums, release["zip_name"])
        result = apply_archive(archive, install_root, expected_sha256=expected)
        result["status"] = "updated"
        return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Update Sales Roleplay Solo from GitHub Releases")
    parser.add_argument("action", choices=("update", "check", "rollback"))
    parser.add_argument("version", nargs="?", help="Optional release tag such as v0.4.1")
    parser.add_argument("--install-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    root = args.install_root.resolve()
    try:
        if args.action == "rollback":
            result = rollback_latest(root)
        elif args.action == "check":
            release = select_release_assets(fetch_release(args.version))
            current = read_version(root)
            result = {
                "installed": current,
                "available": release["version"],
                "update_available": current != release["version"],
            }
        else:
            result = update(root, args.version)
    except UpdateError as exc:
        print(f"UPDATE ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
