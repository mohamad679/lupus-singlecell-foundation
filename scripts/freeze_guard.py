"""The entire freeze mechanism: one function. Not a gate class hierarchy,
not a new stage number -- any script that will touch GSE135779 (sealed
cohort) must call require_valid_freeze() before doing anything else. It
refuses to proceed unless FREEZE.json exists and every hash inside it still
matches the live file on disk.

Usage, at the top of any sealed-cohort script:

    from freeze_guard import require_valid_freeze
    require_valid_freeze()
    # ... only now is it safe to touch GSE135779 ...
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FREEZE_PATH = REPO_ROOT / "FREEZE.json"


class FreezeGuardError(RuntimeError):
    """Raised when FREEZE.json is missing or a frozen file has drifted."""


def _sha256_of(path: Path) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def require_valid_freeze(freeze_path: Path = FREEZE_PATH) -> dict:
    """Return the freeze manifest if valid; raise FreezeGuardError otherwise.

    Checks, in order:
    1. FREEZE.json exists.
    2. Every file listed in frozen_files_sha256 still exists.
    3. Every file's live SHA-256 still matches the recorded hash.

    Any failure raises with a specific, actionable message rather than
    silently proceeding or silently re-freezing.
    """

    if not freeze_path.exists():
        raise FreezeGuardError(
            f"{freeze_path} does not exist. No sealed-cohort (GSE135779) "
            "access is permitted before a freeze is written and reviewed. "
            "Run scripts/16_freeze_manifest.py first."
        )

    with open(freeze_path) as f:
        manifest = json.load(f)

    frozen_files = manifest.get("frozen_files_sha256", {})
    if not frozen_files:
        raise FreezeGuardError(f"{freeze_path} has no frozen_files_sha256 entries.")

    mismatches = []
    for rel_path, expected_hash in frozen_files.items():
        live_path = REPO_ROOT / rel_path
        if not live_path.exists():
            mismatches.append(f"{rel_path}: file no longer exists")
            continue
        live_hash = _sha256_of(live_path)
        if live_hash != expected_hash:
            mismatches.append(
                f"{rel_path}: hash drifted (frozen={expected_hash[:12]}..., "
                f"live={live_hash[:12]}...)"
            )

    if mismatches:
        raise FreezeGuardError(
            "FREEZE.json no longer matches the live files -- refusing to "
            "proceed with any sealed-cohort access. A drifted file means the "
            "pipeline that would score GSE135779 is not the one whose dev-cohort "
            "performance was reported. Mismatches:\n  " + "\n  ".join(mismatches)
        )

    return manifest


if __name__ == "__main__":
    try:
        manifest = require_valid_freeze()
    except FreezeGuardError as exc:
        print(f"FREEZE GUARD: FAIL -- {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"FREEZE GUARD: PASS -- {len(manifest['frozen_files_sha256'])} files verified, "
          f"commit {manifest['commit_sha'][:12]}, frozen at {manifest['timestamp_utc']}")
