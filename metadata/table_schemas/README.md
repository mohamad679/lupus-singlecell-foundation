# Table Schemas

This directory contains CSV schema contracts for future or generated report tables.

Files in this directory may intentionally contain only headers and no data rows.

These files are not analysis results. They define expected columns for pipeline outputs, validation manifests, audit logs, baseline result tables, and related report artifacts.

Populated result or audit tables with real rows should live under:

- `reports/tables/`

Schema-only CSV files should remain under:

- `metadata/table_schemas/`
