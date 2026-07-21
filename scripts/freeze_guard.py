"""The entire freeze mechanism: two functions, one guard, one marker. Not a
gate class hierarchy, not a new stage number -- any script that will touch
GSE135779 (sealed cohort) must call require_valid_freeze() before doing
anything else. It refuses to proceed unless FREEZE.json exists, every hash
inside it still matches the live file on disk, AND the sealed cohort has
not already been opened once (SEALED_OPENED.json does not exist) -- PREREG's
one-look discipline means this happens exactly once, ever, for this freeze.

Usage, at the top of any sealed-cohort script:

    from freeze_guard import require_valid_freeze, mark_sealed_opened
    require_valid_freeze()
    # ... only now is it safe to touch GSE135779 ...
    # ... after Phase 3 completes successfully: ...
    mark_sealed_opened()
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FREEZE_PATH = REPO_ROOT / "FREEZE.json"
SEALED_OPENED_PATH = REPO_ROOT / "SEALED_OPENED.json"


class FreezeGuardError(RuntimeError):
    """Raised when FREEZE.json is missing, a frozen file has drifted, or the
    sealed cohort has already been opened once."""


def _sha256_of(path: Path) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def require_valid_freeze(freeze_path: Path = FREEZE_PATH) -> dict:
    """Return the freeze manifest if valid; raise FreezeGuardError otherwise.

    Checks, in order:
    1. The sealed cohort has not already been opened (SEALED_OPENED.json
       does not exist) -- checked first and unconditionally, since a prior
       opening makes every other check moot.
    2. FREEZE.json exists.
    3. Every file listed in frozen_files_sha256 still exists.
    4. Every file's live SHA-256 still matches the recorded hash.

    Any failure raises with a specific, actionable message rather than
    silently proceeding or silently re-freezing.
    """

    if SEALED_OPENED_PATH.exists():
        with open(SEALED_OPENED_PATH) as f:
            opened_record = json.load(f)
        raise FreezeGuardError(
            f"{SEALED_OPENED_PATH} exists -- the sealed cohort (GSE135779) was "
            f"already opened once, at {opened_record.get('opened_at_utc')}, "
            f"against freeze commit {opened_record.get('freeze_commit_sha', '')[:12]}. "
            "PREREG's one-look discipline means this happens exactly once. "
            "Refusing any further access, regardless of what the prior result showed."
        )

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


def mark_sealed_opened(freeze_path: Path = FREEZE_PATH, results_path: Path | None = None) -> None:
    """Write SEALED_OPENED.json. After this, require_valid_freeze() refuses
    forever (for this freeze). Call only once, after Phase 3 has genuinely
    completed -- not before, not speculatively, and never called again after
    a first successful call (the guard itself would refuse the second call's
    own require_valid_freeze() anyway, but this function does not re-check
    that -- callers are expected to have already gone through the guard).
    """
    with open(freeze_path) as f:
        manifest = json.load(f)
    record = {
        "opened_at_utc": datetime.now(timezone.utc).isoformat(),
        "freeze_commit_sha": manifest["commit_sha"],
        "freeze_timestamp_utc": manifest["timestamp_utc"],
        "results_path": str(results_path) if results_path else None,
        "note": (
            "The sealed cohort (GSE135779) was opened exactly once against "
            "this freeze, per PREREG's one-look discipline. No further "
            "GSE135779 access is permitted under this freeze, regardless of "
            "what the result showed."
        ),
    }
    with open(SEALED_OPENED_PATH, "w") as f:
        json.dump(record, f, indent=2)
    print(f"wrote {SEALED_OPENED_PATH} -- sealed cohort marked opened, "
          "all future require_valid_freeze() calls will now refuse.")


if __name__ == "__main__":
    try:
        manifest = require_valid_freeze()
    except FreezeGuardError as exc:
        print(f"FREEZE GUARD: FAIL -- {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"FREEZE GUARD: PASS -- {len(manifest['frozen_files_sha256'])} files verified, "
          f"commit {manifest['commit_sha'][:12]}, frozen at {manifest['timestamp_utc']}")
