import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).parent.parent / "consultbae.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS people (
            person_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            city TEXT,
            experience_years REAL,
            current_ctc TEXT,
            applied_date TEXT,
            hourly_rate TEXT,
            worker_status TEXT,
            skill_tags TEXT,
            verified TEXT,
            projects_completed INTEGER,
            source_records TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audio_submissions (
            submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER,
            audio_path TEXT,
            duration_seconds REAL,
            sample_rate_khz REAL,
            bitrate_kbps REAL,
            loudness_db REAL,
            noise_score REAL,
            created_at TEXT,
            FOREIGN KEY (person_id) REFERENCES people(person_id)
        )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully.")