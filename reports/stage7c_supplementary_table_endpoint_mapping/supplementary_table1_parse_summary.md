# Supplementary Table 1 parse summary

## Parse result

The official Supplementary Tables workbook for the GSE135779 source paper was retrieved and parsed. Supplementary Table 1 was split into three usable sheets:

| Sheet | Role | Result |
|---|---|---|
| ST1a | cohort-level clinical summary | parsed |
| ST1b | sample-level clinical information | parsed; endpoint-relevant |
| ST1c | sequencing information and QC | parsed |

## ST1b endpoint-relevant fields

ST1b is the key sheet for endpoint mapping. It contains:

- sample identifiers and group labels;
- age, gender, race, ethnicity, and collection year;
- sample-level SLEDAI total score;
- weighted SLEDAI-style clinical/lab components;
- physician notes and symptoms fields;
- medication-at-screening variables;
- nephritis and nephrology class fields;
- laboratory values including complement and anti-dsDNA related fields.

## Proxy endpoint counts

The parsed numeric SLEDAI values support a paper-aligned activity proxy:

| Class | Definition | Count |
|---|---|---:|
| High activity SLE | `SLEDAI > 4` | 16 |
| Low activity SLE | `SLEDAI <= 4` | 23 |
| Excluded unless rule is pre-registered | missing explicit SLEDAI but low observed component totals | 2 |

## Strict endpoint blocker

No explicit sample-level fields were found for:

- flare;
- managed disease;
- stable disease;
- remission;
- inactive disease;
- longitudinal visit status;
- treatment-controlled endpoint status.

Therefore, the proxy endpoint can be used only as high-activity versus low-activity SLE transfer. It cannot be reported as strict external validation of Stage 6 FLARE versus managed SLE.
