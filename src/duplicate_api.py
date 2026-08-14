from flask import Flask, request, jsonify
import sqlite3
from pathlib import Path
from database import get_connection

app = Flask(__name__)

DB_PATH = Path(__file__).parent.parent / "consultbae.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def normalize(value):
    if value is None:
        return ""

    return str(value).strip().lower()


@app.route("/check-duplicate", methods=["POST"])
def check_duplicate():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No JSON data received"
        }), 400

    name = normalize(data.get("name"))
    email = normalize(data.get("email"))
    phone = normalize(data.get("phone"))

    conn = get_connection()
    cursor = conn.cursor()

    # -----------------------------------
    # 1. Check email
    # -----------------------------------

    if email:

        cursor.execute("""
            SELECT *
            FROM people
            WHERE LOWER(TRIM(email)) = ?
            LIMIT 1
        """, (email,))

        person = cursor.fetchone()

        if person:

            conn.close()

            return jsonify({
                "duplicate": True,
                "matched_by": "email",
                "person": dict(person)
            })

    # -----------------------------------
    # 2. Check phone
    # -----------------------------------

    if phone:

        cursor.execute("""
            SELECT *
            FROM people
            WHERE phone = ?
            LIMIT 1
        """, (phone,))

        person = cursor.fetchone()

        if person:

            conn.close()

            return jsonify({
                "duplicate": True,
                "matched_by": "phone",
                "person": dict(person)
            })

    # -----------------------------------
    # 3. Check name
    # -----------------------------------

    if name:

        cursor.execute("""
            SELECT *
            FROM people
            WHERE LOWER(TRIM(name)) = ?
            LIMIT 1
        """, (name,))

        person = cursor.fetchone()

        if person:

            conn.close()

            return jsonify({
                "duplicate": True,
                "matched_by": "name",
                "person": dict(person)
            })

    conn.close()

    # -----------------------------------
    # No duplicate
    # -----------------------------------

    return jsonify({
        "duplicate": False,
        "matched_by": None,
        "message": "New person"
    })
@app.route("/add-person", methods=["POST"])
def add_person():
    data = request.get_json()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO people (name, email, phone)
        VALUES (?, ?, ?)
    """, (
        data.get("name"),
        data.get("email"),
        data.get("phone")
    ))

    conn.commit()
    person_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "success": True,
        "message": "New person added",
        "person_id": person_id
    }), 201


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)