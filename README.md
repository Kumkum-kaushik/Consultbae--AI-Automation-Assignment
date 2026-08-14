# ConsultBae — AI Automation Assignment

## 1. Project Overview

This project is a submission for the ConsultBae AI Automation Assignment. It has three working parts that share a single SQLite database (`consultbae.db`):

1. **A merged people database** — three inconsistent source CSVs (a Naukri applicant export, a gig-worker sheet, and a CBNexus contacts export) are cleaned, normalized, and entity-matched into one `people` table.
2. **An n8n duplicate-check automation** — a Flask API exposes duplicate-checking and person-creation endpoints. An n8n workflow calls this API from a webhook so that a new submission can be checked against the merged `people` table before being added.
3. **A Flask audio collection application** — a small web app that collects a name, phone number, and a WAV recording, extracts audio metadata (duration, sample rate, bitrate, loudness), stores the file, links it to a person in the same `people` table, and lists all submissions with in-browser playback.

## 2. Project Structure

```
Consultbae-AI Automation Assignment/
├── app/                                  # placeholder directory (currently empty)
├── data/
│   ├── source1_naukri_applicants.csv     # Task 1 source: Naukri applicants
│   ├── source2_gig_workers.csv           # Task 1 source: gig workers
│   └── source3_cbnexus_contacts.csv      # Task 1 source: CBNexus contacts
├── docs/
│   └── data_issues_report.md             # Task 4 report
├── n8n/                                  # placeholder directory (currently empty — the
│                                          # workflow itself lives inside the n8n editor,
│                                          # not as an exported file in this repo)
├── src/
│   ├── audio_app.py         # Task 3 — Flask audio collection app (port 5001)
│   ├── check_database.py    # utility: dumps the people table to stdout
│   ├── cleaning.py          # Task 1 — field-level normalization functions
│   ├── data_quality.py      # utility: prints missing values / dtypes / dup counts per CSV
│   ├── database.py          # Task 1 — creates the SQLite schema
│   ├── duplicate_api.py     # Task 2 — Flask API used by the n8n workflow (port 5000)
│   ├── inspect_data.py      # utility: same inspection helper as data_quality.py
│   ├── matching.py          # Task 1 — exact_match() / find_matches() entity matching
│   ├── match_sources.py     # utility: prints matches found between source pairs
│   ├── merge_data.py        # Task 1 — builds unified people and writes them to SQLite
│   ├── prepare_data.py      # Task 1 — loads + cleans the three CSVs
│   ├── test_cleaning.py     # manual smoke test for cleaning.py
│   └── test_matching.py     # manual smoke test for matching.py
├── templates/
│   ├── submissions.html     # Task 3 — submissions list + audio player
│   └── upload.html          # Task 3 — upload form
├── uploads/                 # stored .wav files (named as <uuid4>.wav)
├── consultbae.db            # SQLite database shared by Task 1 and Task 3
└── README.md
```

## 3. Task 1 — Data Merge

**Sources:** `data/source1_naukri_applicants.csv`, `data/source2_gig_workers.csv`, `data/source3_cbnexus_contacts.csv`. Each file uses different column names, casing, and formats for the same kinds of data (name, contact info, city). Full findings are in [docs/data_issues_report.md](docs/data_issues_report.md).

**Database:** `consultbae.db` (SQLite), created by `src/database.py`. It defines two tables:

- `people` — `person_id, name, email, phone, city, experience_years, current_ctc, applied_date, hourly_rate, worker_status, skill_tags, verified, projects_completed, source_records`. `source_records` records which of the three sources contributed to that person (e.g. `"CBNexus, Gig Workers, Naukri"`).
- `audio_submissions` — used by Task 3, with a `person_id` foreign key back into `people`.

**Pipeline:**

1. `prepare_data.py` loads the three CSVs with pandas and applies the normalization functions from `cleaning.py` to produce `*_clean` columns (`name_clean`, `email_clean`, `phone_clean`, `city_clean`, plus `status_clean`/`skills_clean` for gig workers and `verified_clean` for CBNexus). Rows that are entirely blank are dropped with `dropna(how="all")`.
2. `matching.py` provides `exact_match(record1, record2)`, which checks, in order: **email match → phone match → name + city match**. `find_matches()` compares two whole source frames using this rule (used by `match_sources.py` for inspection, not by the merge itself).
3. `merge_data.py` builds the unified list: it walks all three cleaned sources in order (Naukri, then Gig Workers, then CBNexus) and, for each row, tries `exact_match()` against every person already added. If a match is found, `merge_person()` fills in only the fields that are currently empty on the existing person (it never overwrites a value that's already set) and adds the new source to `source_records`. If no match is found, the row becomes a new person. The result is written to the `people` table by `save_to_database()`.

**Key normalization logic actually implemented (`cleaning.py`):**

- `normalize_name` — lowercases and collapses repeated whitespace.
- `normalize_email` — lowercases and trims.
- `normalize_phone` — strips all non-digit characters; if the result is 12 digits starting with `91`, the `91` prefix is dropped.
- `normalize_city` — lowercases, then maps a fixed set of variants: `gurgaon → gurugram`, `bangalore → bengaluru` (other values, including `delhi`, `new delhi`, and `delhi ncr`, are lowercased but kept as separate values).
- `normalize_status` — lowercases.
- `normalize_verified` — maps `y`/`yes` → `yes` and `n`/`no` → `no`.
- `normalize_skills` — splits the comma-separated skill list, trims and lowercases each skill, rejoins.

## 4. Task 2 — n8n Automation

`src/duplicate_api.py` is a Flask API (default `http://127.0.0.1:5000`) with two endpoints that the n8n workflow calls:

- `POST /check-duplicate` — accepts `{name, email, phone}`, normalizes each with `str(value).strip().lower()`, and checks the `people` table in order: `LOWER(TRIM(email)) = ?`, then `phone = ?`, then `LOWER(TRIM(name)) = ?`. Returns `{"duplicate": true, "matched_by": "...", "person": {...}}` on a hit, or `{"duplicate": false, "matched_by": null, "message": "New person"}` otherwise.
- `POST /add-person` — inserts a new row into `people` using only `name`, `email`, and `phone`.

**The workflow itself is built and run in n8n**, not as a script in this repo (the `n8n/` folder is a placeholder — no workflow was exported into it). Its shape is:

```
Webhook  →  HTTP Request (POST /check-duplicate)  →  IF (duplicate == true)
                                                        ├─ true  → Respond: duplicate found
                                                        └─ false → HTTP Request (POST /add-person) → Respond: person added
```

This is intentionally not a pure-code solution — the orchestration (webhook intake, branching, and response shaping) is done inside n8n, and `duplicate_api.py` only supplies the two HTTP endpoints it calls.

## 5. Task 3 — Audio Collection App

`src/audio_app.py` is a Flask app (default `http://127.0.0.1:5001`) with the following behavior:

- `GET /` — renders `templates/upload.html`, a form for **name**, **phone**, and a **WAV file** upload.
- `POST /submit-audio` — requires name, phone, and an audio file ending in `.wav`. The file is saved to `uploads/` under a generated `uuid4().hex` filename (the original filename is discarded). `analyze_wav()` reads the file with the standard-library `wave` module and NumPy to compute:
  - `duration` (seconds, from frame count / sample rate)
  - `sample_rate_khz`
  - `bitrate_kbps` (`sample_rate × sample_width × 8 × channels`)
  - `loudness_db` (20·log10 of RMS amplitude relative to the sample width's max value)
  
  The app then looks up a matching person in `people` by exact `name`/`phone` (`LOWER(TRIM(name)) = LOWER(TRIM(?)) AND phone = ?`); if none exists, it inserts a new person with just `name` and `phone`. A row is then inserted into `audio_submissions`, linked via `person_id`.
- `GET /submissions` — renders `templates/submissions.html`, listing every submission (name, phone, duration, sample rate, bitrate, loudness) joined against `people`, with an HTML `<audio controls>` player per row.
- `GET /audio/<filename>` — serves the stored WAV file from `uploads/` so the player in `/submissions` can play it back.

## 6. Task 4 — Data Issues Report

The full list of data quality problems found in the three source CSVs, and how the pipeline in `src/cleaning.py`, `src/matching.py`, and `src/merge_data.py` handles (or does not handle) each one, is documented separately:

**[docs/data_issues_report.md](docs/data_issues_report.md)**

## 7. Setup

The project uses a local virtual environment (`venv/`). Dependencies actually imported by the code:

| Package | Used by |
|---|---|
| `flask` | `duplicate_api.py`, `audio_app.py` |
| `pandas` | `prepare_data.py`, `merge_data.py`, `data_quality.py`, `inspect_data.py`, `match_sources.py` |
| `numpy` | `audio_app.py` (WAV sample analysis) |

`sqlite3`, `wave`, `uuid`, `pathlib`, and `re` are all Python standard library and need no install.

```bash
python -m venv venv
venv\Scripts\activate          # Windows

pip install flask pandas numpy
```

## 8. How to Run

All scripts in `src/` use plain module imports (e.g. `from prepare_data import ...`), so run them from inside `src/`.

**Build the database (Task 1):**

```bash
cd src
python database.py      # creates people + audio_submissions tables if they don't exist
python merge_data.py    # cleans, matches, and writes the unified people to the database
```

**Inspect the result:**

```bash
python check_database.py
```

**Run the duplicate-check API (Task 2):**

```bash
python duplicate_api.py
# -> http://127.0.0.1:5000
#    POST /check-duplicate
#    POST /add-person
```

**Run the audio collection app (Task 3):**

```bash
python audio_app.py
# -> http://127.0.0.1:5001
#    GET  /                upload form
#    POST /submit-audio
#    GET  /submissions
#    GET  /audio/<filename>
```

**n8n:** run n8n separately (e.g. `npx n8n` or the desktop app) and import/build the workflow described in Section 9 below, pointing its HTTP Request nodes at the running `duplicate_api.py` instance.

## 9. n8n Configuration

- **Webhook node** — receives the incoming submission (`name`, `email`, `phone`) that should be checked. Its URL is generated by n8n itself when the workflow is activated and is not stored in this repository.
- **HTTP Request node** — `POST http://127.0.0.1:5000/check-duplicate` with the webhook payload as the JSON body.
- **IF node** — branches on the response's `duplicate` boolean.
  - **True** → responds to the webhook caller that the person already exists (using the returned `matched_by` and `person`).
  - **False** → a second **HTTP Request node** calls `POST http://127.0.0.1:5000/add-person`, then a **Respond to Webhook** node confirms the new person was added.

No API keys, tokens, or credentials are required by either Flask service — both run unauthenticated on localhost, so nothing sensitive needs to be configured in n8n beyond the two URLs above.

## 10. Stuck Log

### Issue 1 — n8n webhook testing

**Problem:** Test/production webhook behavior caused confusion during Postman testing.

**Resolution:** Verified the webhook workflow and used the correct published endpoint for testing.

### Issue 2 — SQLite audio schema mismatch

**Problem:** `audio_app.py` attempted to insert columns that did not match the existing `audio_submissions` schema.

**Resolution:** Inspected the SQLite schema and aligned the audio application with the actual database structure.

### Issue 3 — Audio playback

**Problem:** Audio metadata appeared correctly but the browser player showed 0:00 / could not play the file.

**Resolution:** Aligned the stored audio filename/path with the Flask file-serving route and submissions template.

## 11. Known Limitations

- **Phone matching relies on exact string equality outside the Task 1 merge.** `duplicate_api.py` and `audio_app.py` compare `phone` as-is (only trimmed/lowercased, not digit-normalized), so the same number in a different format (`+91-...` vs `9000000...`) will not be recognized as a duplicate through those two endpoints.
- **`normalize_city` only merges two city-name pairs.** `gurgaon → gurugram` and `bangalore → bengaluru` are mapped, but `delhi`, `new delhi`, and `delhi ncr` are treated as three distinct cities, which can prevent a name+city match across sources.
- **Dates and CTC/rate values are stored as-is.** `applied_date` keeps whatever format was in the source row (e.g. `24-07-2026`, `2026-08-08`, `7 Jul 2026`), and `current_ctc` is stored without unit normalization even though the source data mixes absolute rupee figures with much smaller decimal values.
- **Entity matching is a linear scan.** `merge_data.py` compares every new row against every person already added; this is fine at the current data size but does not scale.
- **`POST /add-person` only stores `name`, `email`, and `phone`** — any other fields sent to it are ignored, since the SQL insert lists just those three columns.
- **`noise_score` is defined in the `audio_submissions` schema but never computed.** `analyze_wav()` does not return a `noise_score`, so the column is always stored as `NULL`.
- **Both Flask services run without authentication**, which is acceptable for local/demo use but not for a public deployment.

## 12. Demo

The screen recording should show, in order:

1. The n8n workflow open in the editor (webhook → HTTP Request → IF → HTTP Request/Respond).
2. A duplicate-person test: submitting a payload that matches an existing person in `people` and getting the "duplicate" response back.
3. A new-person test: submitting a payload for someone not in `people` and confirming they are added via `/add-person`.
4. Uploading a WAV file through the Task 3 upload form (`/`).
5. The extracted metadata (duration, sample rate, bitrate, loudness) shown after submission.
6. The `/submissions` page, including playing the uploaded audio back in the browser.
