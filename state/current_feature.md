# Current Feature

## STAGE4-F001 - Real embedding artifact validation

Status: in_progress
Branch: `feat/stage4-real-artifact-directory-manifest`

## Objective

Start Stage 4 by validating a user-supplied local real embedding artifact path
through safe metadata checks only.

This feature defines a guarded manifest and filesystem metadata contract for the
existing local embedding artifact produced outside the repository.

## Allowed in this feature

- Record a local artifact path string.
- Check whether the local path exists.
- Check whether the path is a regular file or directory.
- Record file size metadata.
- Count top-level `.npy` files in a local directory.
- Summarize filename categories without opening embedding payloads.
- Compute a checksum only when explicitly requested.
- Validate safe manifest fields such as dataset id, artifact format, record
  level, donor/cell identifier column names, embedding dimension, and safety
  flags.

## Not allowed in this feature

No real embedding artifact is committed.
No model artifact is committed.
No AnnData files are loaded.
No downloads are performed.
No Geneformer execution is performed.
No tokenizer execution is performed.
No embedding extraction is performed.
No embedding payload table is parsed.
No `.npy` embedding payload is loaded.
No real donor-level aggregation is performed.
No baseline feature extraction is performed.
No scalers are fit.
No models are fit.
No real metrics are computed.
No training is performed.
No external validation is performed.
No performance claims are added.

## Local artifact rule

The real embedding artifact remains outside Git. Only path, filesystem metadata,
checksum metadata, schema/status fields, and audit notes may be recorded in a
safe manifest.

The local artifact has been observed outside the repository as a directory of 261 `.npy` files totaling 344.12 MB. The absolute local path is not committed.
