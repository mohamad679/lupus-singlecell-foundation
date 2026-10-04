"""Phase 3 entry point: the sealed-cohort (GSE135779) opening.

NOT YET IMPLEMENTED beyond the freeze guard. This file exists now so that
require_valid_freeze() is demonstrably wired into the actual script that
will eventually touch GSE135779, rather than only proven to work in
isolation (scripts/freeze_guard.py's own __main__ block). No GSE135779
expression, cell-level, or per-sample clinical data is loaded by this file
as it stands -- it stops immediately after the guard check.

When Phase 3 is authorized to actually run, the real logic goes after the
guard call below: stream/download GSE135779 (once, per PREREG's
freeze/one-look discipline), harmonize via
results/gene_space_intersection.txt (already computed, real), score each
of the three PREREG arms using FREEZE.json's frozen C values and the exact
model family recorded there, and report patient-level AUROC/CI/permutation
p on the sealed cohort. None of that is written yet.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from freeze_guard import FreezeGuardError, require_valid_freeze  # noqa: E402


def main() -> int:
    try:
        manifest = require_valid_freeze()
    except FreezeGuardError as exc:
        print(f"REFUSING TO PROCEED: {exc}", file=sys.stderr)
        return 1

    print(f"Freeze verified: commit {manifest['commit_sha'][:12]}, "
          f"{len(manifest['frozen_files_sha256'])} files, "
          f"frozen at {manifest['timestamp_utc']}.")
    print()
    print("Phase 3 body is not yet implemented past this point. No GSE135779 "
          "data has been loaded. Stopping here by design.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
