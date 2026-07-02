# GSE135779 manifest scaffold

## Required table

Create one row per GSE135779 sample before scoring.

Required columns:

- `sample_id`
- `group`
- `age`
- `sledai`
- `proxy_label`
- `included_primary`
- `exclusion_reason`

## Proxy label rules

- SLE sample with `SLEDAI > 4`: positive proxy class.
- SLE sample with `SLEDAI <= 4`: negative proxy class.
- Missing explicit SLEDAI: exclude from primary proxy scoring.
- Healthy controls: exclude from primary proxy scoring.

## Status

Scaffold created. The real manifest is still pending the parsed ST1b table as local input.
