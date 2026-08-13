import sqlite3
from pathlib import Path

from prepare_data import (
    load_sources,
    clean_naukri,
    clean_gig_workers,
    clean_cbnexus
)

from matching import exact_match


DB_PATH = Path(__file__).parent.parent / "consultbae.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def normalize_value(value):
    if value is None:
        return None

    try:
        if str(value).lower() == "nan":
            return None
    except:
        pass

    return value


def create_person_from_naukri(row):

    return {
        "name": normalize_value(row.get("Full Name")),
        "email": row.get("email_clean"),
        "phone": row.get("phone_clean"),
        "city": row.get("city_clean"),
        "experience_years": normalize_value(
            row.get("Experience (Years)")
        ),
        "current_ctc": normalize_value(
            row.get("Current CTC")
        ),
        "applied_date": normalize_value(
            row.get("Applied Date")
        ),
        "hourly_rate": None,
        "worker_status": None,
        "skill_tags": normalize_value(
            row.get("Skills")
        ),
        "verified": None,
        "projects_completed": None,
        "source": "Naukri"
    }


def create_person_from_gig(row):

    return {
        "name": normalize_value(row.get("worker_name")),
        "email": row.get("email_clean"),
        "phone": None,
        "city": row.get("city_clean"),
        "experience_years": None,
        "current_ctc": None,
        "applied_date": None,
        "hourly_rate": normalize_value(
            row.get("rate")
        ),
        "worker_status": row.get("status_clean"),
        "skill_tags": row.get("skills_clean"),
        "verified": None,
        "projects_completed": None,
        "source": "Gig Workers"
    }


def create_person_from_cbnexus(row):

    return {
        "name": normalize_value(row.get("Name")),
        "email": None,
        "phone": row.get("phone_clean"),
        "city": row.get("city_clean"),
        "experience_years": None,
        "current_ctc": None,
        "applied_date": None,
        "hourly_rate": None,
        "worker_status": None,
        "skill_tags": None,
        "verified": row.get("verified_clean"),
        "projects_completed": normalize_value(
            row.get("Projects Completed")
        ),
        "source": "CBNexus"
    }


def records_match(person, new_person):

    matched, method = exact_match(
        person,
        new_person
    )

    return matched, method


def merge_person(existing, new_person):

    for key in [
        "name",
        "email",
        "phone",
        "city",
        "experience_years",
        "current_ctc",
        "applied_date",
        "hourly_rate",
        "worker_status",
        "skill_tags",
        "verified",
        "projects_completed"
    ]:

        if not existing.get(key) and new_person.get(key):
            existing[key] = new_person[key]

    existing["source_records"].add(
        new_person["source"]
    )

    return existing

def build_unified_people():

    naukri, gig_workers, cbnexus = load_sources()

    naukri = clean_naukri(naukri)
    gig_workers = clean_gig_workers(gig_workers)
    cbnexus = clean_cbnexus(cbnexus)

    unified_people = []

    sources = [
        (naukri, create_person_from_naukri),
        (gig_workers, create_person_from_gig),
        (cbnexus, create_person_from_cbnexus)
    ]

    for dataframe, converter in sources:

        for _, row in dataframe.iterrows():

            new_person = converter(row)

            found_match = False

            for existing_person in unified_people:

                matched, method = records_match(
                    existing_person,
                    new_person
                )

                if matched:

                    merge_person(
                        existing_person,
                        new_person
                    )

                    found_match = True

                    break

            if not found_match:

                new_person["source_records"] = {
                    new_person["source"]
                }

                unified_people.append(
                    new_person
                )

    return unified_people

def save_to_database(people):

    conn = get_connection()
    cursor = conn.cursor()

    for person in people:

        cursor.execute("""
            INSERT INTO people (
                name,
                email,
                phone,
                city,
                experience_years,
                current_ctc,
                applied_date,
                hourly_rate,
                worker_status,
                skill_tags,
                verified,
                projects_completed,
                source_records
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            person["name"],
            person["email"],
            person["phone"],
            person["city"],
            person["experience_years"],
            person["current_ctc"],
            person["applied_date"],
            person["hourly_rate"],
            person["worker_status"],
            person["skill_tags"],
            person["verified"],
            person["projects_completed"],
            ", ".join(
                sorted(person["source_records"])
            )
        ))

    conn.commit()
    conn.close()

if __name__ == "__main__":

    people = build_unified_people()

    print(
        f"\nUnified people count: {len(people)}"
    )

    save_to_database(people)

    print(
        "Unified people successfully saved to SQLite."
    )