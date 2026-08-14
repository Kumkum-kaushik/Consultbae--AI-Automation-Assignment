# Task 4 — Data Issues Report

## 1. Overview

The assignment provides three source datasets from different systems:

1. `source1_naukri_applicants.csv` — 42 data rows, 8 columns
2. `source2_gig_workers.csv` — 32 data rows, 6 columns
3. `source3_cbnexus_contacts.csv` — 31 data rows, 5 columns

The datasets contain overlapping people and intentionally inconsistent data. The main goal of the data-cleaning/merge work was to create a usable common database while preserving the source attributes needed by the application.

The issues below were identified by inspecting the actual source files.

---

## 2. Issues Found

| Source | Column | Issue | Example | Action / Handling |
|---|---|---|---|---|
| Naukri | Full Name | Duplicate record | `Rohit Verma` appears twice with the same email and phone | Treat as the same person during entity matching; avoid creating a second person record |
| Naukri | Full Name / Email / Phone | Same name with conflicting identifiers | `Nikhil Chopra` appears twice; one record has `alt.nikhil.chopra70@example.com` while the other has `nikhil.chopra70@example.com`, but both use phone `09000000103` | Phone is a useful matching signal; conflicting email values should not automatically create two people |
| Naukri | Phone | Country-code/format inconsistency | `+919000000254`, `919000000260`, `09000000287`, `9000000237` | Phone values need normalization before robust cross-source matching; current duplicate API compares the normalized input directly |
| Naukri | City | Case/format inconsistency | `GURGAON`, `gurugram`, `Delhi NCR`, `new delhi`, `Bengaluru`, `Bangalore` | Preserve source value but normalize/standardize when using city for analysis |
| Naukri | Applied Date | Multiple date formats | `24-07-2026`, `2026-08-08`, `07/13/2026`, `7 Jul 2026` | Dates should be parsed into one standard format before analytics |
| Naukri | Applied Date | Future/suspicious dates relative to the assignment run date | `21-08-2026`, `22-08-2026`, `19-08-2026` | Flag for validation rather than silently changing the source value |
| Naukri | Current CTC | Strongly inconsistent numeric representation/scale | `4.2`, `8.3`, `11.2` versus `417964`, `775670`, `1195422` | Treat as a unit/scale issue; values should be standardized before salary comparisons |
| Gig Workers | Entire row | Malformed/misaligned row | Row beginning `react, javascript, mysql` has values shifted into the wrong columns | Flag as malformed and exclude/correct before reliable ingestion |
| Gig Workers | Entire row | Blank row | One row contains no values | Ignore/remove blank row during ingestion |
| Gig Workers | email_id | Case inconsistency | `VARUN.SAXENA21@EXAMPLE.IN`, `DEEPAK.NAIR44@EXAMPLE.COM` | Lowercase + trim for matching; the duplicate-check API uses `LOWER(TRIM(email))` |
| Gig Workers | status | Case inconsistency | `Active`, `active`, `ACTIVE`, `Inactive`, `paused` | Normalize categorical values to a controlled vocabulary |
| Gig Workers | location | Case inconsistency | `Pune`, `PUNE`, `pune`, `Gurgaon`, `gurugram`, `New Delhi` | Normalize case and optionally map equivalent city names |
| Gig Workers | rate | Mixed units | `1415/hr`, `15k/month`, `72k/month`, `79k/month` | Parse numeric amount and period separately; do not compare raw values directly |
| Gig Workers | worker_name / email_id | Repeated person pattern | `Isha Chopra` appears in a normal row and again in the malformed row | Do not double-count the malformed row as a separate worker |
| Gig Workers | worker_name / email_id | Same name with different identifiers | `Deepak Nair` occurs with `deepak.nair44@example.com` and `DEEPAK.NAIR57@EXAMPLE.IN` | Requires identifier-based matching rather than name-only matching |
| CBNexus | Entire row | Header row embedded in data | Row containing `Name`, `Phone Number`, `City`, `Verified`, `Projects Completed` | Remove/ignore the embedded header before loading data |
| CBNexus | Phone Number | Multiple phone formats | `9000000268`, `919000000231`, `+91-9000000131` | Normalize to a canonical phone representation before cross-source matching |
| CBNexus | Name | Case inconsistency | `RITU SHARMA`, `RAHUL MALHOTRA`, `KARAN BHATIA`, `MANISH BHATIA` | Lowercase + trim for matching; duplicate API uses `LOWER(TRIM(name))` |
| CBNexus | City | Case inconsistency | `Noida`, `NOIDA`, `pune`, `PUNE`, `GURGAON` | Normalize categorical values |
| CBNexus | Verified | Multiple representations | `Y`, `Yes`, `yes`, `N`, `No` | Convert to a controlled boolean/Yes-No representation |
| CBNexus | Projects Completed | Header contamination | Embedded header row contains `Projects Completed` in the numeric column | Remove malformed/header row before numeric conversion |
| CBNexus | Name / Phone | Ambiguous repeated person name | `Arjun Mehta` appears twice with different phone numbers (`9000000131` and `9000000272`) | Do not merge based on name alone; require stronger identifiers |

---

## 3. Duplicate and Entity-Matching Issues

A major challenge is that there is no single ID common to all three source systems.

### Exact duplicate

`Rohit Verma` is duplicated in the Naukri source with the same:

- email: `rohit.verma13@mailtest.example.org`
- phone: `9000000294`

These rows should represent one person rather than two database records.

### Conflicting identifiers

`Nikhil Chopra` appears twice in Naukri:

- `alt.nikhil.chopra70@example.com` + `09000000103`
- `nikhil.chopra70@example.com` + `09000000103`

The shared phone is a strong signal that these records refer to the same person, while the email difference should be retained as a data-quality warning rather than ignored.

### Cross-source matching

The same people appear across sources with differences in:

- name capitalization
- phone country-code formatting
- city capitalization
- email capitalization

The duplicate API therefore normalizes email and name using `LOWER(TRIM(...))` and checks phone as a separate identifier.

The matching order used by the duplicate API is:

1. Email
2. Phone
3. Name

This provides a deterministic duplicate check while giving stronger identifiers priority over name-only matching.

### Matching limitation

Phone values are not yet converted to a single canonical digit format everywhere. For example:

- `9000000131`
- `919000000131`
- `+91-9000000131`

can represent the same phone number.

This is therefore documented as a remaining normalization improvement rather than claiming it has been fully solved.

---

## 4. Missing and Blank Data

The following issues were observed:

### Gig Workers

There is one completely blank row in `source2_gig_workers.csv`.

**Handling:** The row has no usable person information and should be ignored during ingestion.

### Other missing values

No broad missing-value problem was observed in the displayed Naukri and CBNexus records. Therefore, missing values are not reported as a major issue for those files.

---

## 5. Formatting and Normalization Issues

### Names

Names use mixed capitalization:

- `RITU SHARMA`
- `Ritu Sharma`
- `rahul...`-style values in other fields

The matching logic normalizes names with:

```python
LOWER(TRIM(name))
```

This prevents case and surrounding-space differences from blocking a match.

### Emails

Emails have mixed capitalization in the Gig Workers dataset.

The duplicate API normalizes email using:

```python
LOWER(TRIM(email))
```

### Phone numbers

Phone values use several formats:

```text
9000000268
919000000231
+91-9000000131
09000000287
```

These should ultimately be converted to one canonical representation.

### Cities

Examples include:

```text
Pune
PUNE
pune
Gurgaon
gurugram
Bangalore
Bengaluru
```

Case can be normalized safely. Some names such as Gurgaon/Gurugram and Bangalore/Bengaluru may require a business rule before being treated as identical.

### Dates

Naukri contains several date formats, including:

```text
2026-08-08
24-07-2026
07/13/2026
7 Jul 2026
```

These should be parsed to a standard ISO-style date before analysis.

### Rates

Gig worker rates mix hourly and monthly units:

```text
1415/hr
15k/month
72k/month
79k/month
```

A numeric amount alone is therefore insufficient. The period/unit must be stored separately.

---

## 6. Malformed Records

The most significant malformed record is in the Gig Workers dataset.

The row beginning with:

```text
react, javascript, mysql
```

is shifted across columns. It results in values such as an email appearing under `worker_name`, `Isha Chopra` appearing under `rate`, and `active` appearing under `skill_tags`.

This record cannot safely be interpreted using the normal schema.

**Action:** Flag it as malformed and prevent it from being treated as a normal independent worker record.

CBNexus also contains a header row inside the data:

```text
Name | Phone Number | City | Verified | Projects Completed
```

This row must be removed before type conversion or ingestion.

---

## 7. Issues Not Automatically Resolved

The following are documented limitations rather than silently corrected:

1. Phone numbers with `+91`, `91`, leading zeroes, and plain 10-digit formats require canonicalization.
2. CTC values appear to use inconsistent units/scales and require business confirmation before conversion.
3. Hourly and monthly worker rates require separate normalization rules.
4. `Gurgaon` vs `Gurugram` and `Bangalore` vs `Bengaluru` should only be merged when the application's location-normalization rule explicitly allows it.
5. Same-name records with different identifiers, such as the two `Arjun Mehta` CBNexus records, should not be merged based on name alone.
6. Future-looking application dates should be validated against the source-system timestamp rather than automatically deleted.

These are intentionally documented because silently changing source data can create incorrect person matches.

---

## 8. Final Data Quality Assessment

The three datasets contain several classes of quality problems:

- duplicate records
- conflicting identifiers
- inconsistent phone formats
- inconsistent capitalization
- inconsistent city names
- inconsistent date formats
- mixed salary/rate units
- malformed rows
- embedded header rows
- categorical-value inconsistencies

The implemented duplicate-checking API provides deterministic matching based on normalized email/name plus phone checks. The audio application also links submissions to the common `people` table using `person_id`, keeping person information separate from audio metadata.

The remaining normalization limitations are explicitly documented rather than hidden. This is important because aggressive fuzzy matching or unit conversion without business rules could incorrectly merge different workers or change the meaning of source values.
