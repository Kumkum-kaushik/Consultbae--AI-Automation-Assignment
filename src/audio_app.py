from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import sqlite3
from pathlib import Path
import wave
import numpy as np
import uuid
from flask import send_from_directory

BASE_DIR = Path(__file__).parent.parent

app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))

DB_PATH = BASE_DIR / "consultbae.db"
UPLOAD_FOLDER = BASE_DIR / "uploads"

UPLOAD_FOLDER.mkdir(exist_ok=True)


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS audio_submissions (
            submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER,
            audio_path TEXT NOT NULL,
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

def analyze_wav(filepath):
    with wave.open(str(filepath), "rb") as audio:

        channels = audio.getnchannels()
        sample_rate = audio.getframerate()
        sample_width = audio.getsampwidth()
        frame_count = audio.getnframes()

        duration = frame_count / sample_rate

        raw_data = audio.readframes(frame_count)

    # Convert audio bytes to numpy values
    if sample_width == 1:
        samples = np.frombuffer(raw_data, dtype=np.uint8).astype(np.float32)
        samples = samples - 128

    elif sample_width == 2:
        samples = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32)

    elif sample_width == 4:
        samples = np.frombuffer(raw_data, dtype=np.int32).astype(np.float32)

    else:
        raise ValueError("Unsupported WAV sample width")

    if len(samples) == 0:
        loudness = -100.0
    else:
        rms = np.sqrt(np.mean(samples ** 2))

        max_value = float(2 ** (sample_width * 8 - 1))

        if rms > 0:
            loudness = 20 * np.log10(rms / max_value)
        else:
            loudness = -100.0

    bitrate = sample_rate * sample_width * 8 * channels

    return {
        "duration": round(duration, 2),
        "sample_rate_khz": round(sample_rate / 1000, 2),
        "bitrate_kbps": round(bitrate / 1000, 2),
        "loudness_db": round(float(loudness), 2)
    }


@app.route("/")
def home():
    return render_template("upload.html")


@app.route("/submit-audio", methods=["POST"])
def submit_audio():

    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    audio_file = request.files.get("audio")

    if not name or not phone or not audio_file:
        return "Name, phone and audio are required", 400

    original_name = audio_file.filename

    if not original_name.lower().endswith(".wav"):
        return "Please upload a WAV audio file", 400

    filename = f"{uuid.uuid4().hex}.wav"
    filepath = UPLOAD_FOLDER / filename

    audio_file.save(filepath)

    try:
        metadata = analyze_wav(filepath)
    except Exception as e:
        filepath.unlink(missing_ok=True)
        return f"Could not process audio: {str(e)}", 400

    conn = get_connection()

    # Find person from Task 1 database
    cursor = conn.execute("""
        SELECT person_id
        FROM people
        WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))
        AND phone = ?
        LIMIT 1
    """, (name, phone))

    person = cursor.fetchone()

    if person:
        person_id = person["person_id"]
    else:
        # Person doesn't exist yet, so create them
        cursor = conn.execute("""
            INSERT INTO people (name, phone)
            VALUES (?, ?)
    """, (name, phone))

        person_id = cursor.lastrowid

    conn.execute("""
        INSERT INTO audio_submissions (
            person_id,
            audio_path,
            duration_seconds,
            sample_rate_khz,
            bitrate_kbps,
            loudness_db,
            noise_score,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (
        person_id,
        filename,
        metadata["duration"],
        metadata["sample_rate_khz"],
        metadata["bitrate_kbps"],
        metadata["loudness_db"],
        metadata.get("noise_score")
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("submissions"))


@app.route("/submissions")
def submissions():

    conn = get_connection()

    rows = conn.execute("""
        SELECT
            a.submission_id,
            p.name,
            p.phone,
            a.audio_path,
            a.duration_seconds,
            a.sample_rate_khz,
            a.bitrate_kbps,
            a.loudness_db,
            a.noise_score,
            a.created_at
        FROM audio_submissions a
        LEFT JOIN people p
            ON a.person_id = p.person_id
        ORDER BY a.submission_id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "submissions.html",
        submissions=rows
    )
@app.route("/audio/<filename>")
def audio(filename):
    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )


if __name__ == "__main__":
    create_table()

    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )