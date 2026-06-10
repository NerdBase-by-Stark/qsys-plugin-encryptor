#!/usr/bin/env python3
"""Verify the vendored QSC tool files against tool-checksums.sha256.

Run from qplug-encryptor-pyside6/ (CI and BUILD.bat both call it after fetching
the tool into vendor/plugin-tool/). Exits non-zero on any missing file, checksum
mismatch (tampering / version drift), or a file present but unlisted.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "tool-checksums.sha256"
VENDOR = ROOT / "vendor" / "plugin-tool"


def main() -> int:
    expected: dict[str, str] = {}
    for line in MANIFEST.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        digest, name = line.split(None, 1)
        expected[name.strip()] = digest.lower()

    bad = 0
    for name, want in expected.items():
        f = VENDOR / name
        if not f.is_file():
            print(f"MISSING  {name}")
            bad += 1
            continue
        got = hashlib.sha256(f.read_bytes()).hexdigest()
        if got != want:
            print(f"MISMATCH {name}")
            bad += 1
        else:
            print(f"ok       {name}")

    if bad:
        print(f"{bad} checksum failure(s) - aborting (tool tampered or version drift)")
        return 1
    print(f"all {len(expected)} tool checksums OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
