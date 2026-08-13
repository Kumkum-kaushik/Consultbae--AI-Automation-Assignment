import pandas as pd
from pathlib import Path

from cleaning import (
    normalize_name,
    normalize_email,
    normalize_phone,
    normalize_city,
    normalize_status,
    normalize_verified,
    normalize_skills,
)


DATA_DIR = Path(__file__).parent.parent / "data"


def load_sources():

    naukri = pd.read_csv(
        DATA_DIR / "source1_naukri_applicants.csv"
    )

    gig_workers = pd.read_csv(
        DATA_DIR / "source2_gig_workers.csv"
    )

    cbnexus = pd.read_csv(
        DATA_DIR / "source3_cbnexus_contacts.csv"
    )

    return naukri, gig_workers, cbnexus


def clean_naukri(df):

    df = df.copy()

    # Remove completely empty rows
    df = df.dropna(how="all")

    df["name_clean"] = df["Full Name"].apply(normalize_name)
    df["email_clean"] = df["Email"].apply(normalize_email)
    df["phone_clean"] = df["Phone"].apply(normalize_phone)
    df["city_clean"] = df["City"].apply(normalize_city)

    return df


def clean_gig_workers(df):

    df = df.copy()

    # Remove completely empty rows
    df = df.dropna(how="all")

    df["name_clean"] = df["worker_name"].apply(normalize_name)
    df["email_clean"] = df["email_id"].apply(normalize_email)
    df["city_clean"] = df["location"].apply(normalize_city)
    df["status_clean"] = df["status"].apply(normalize_status)
    df["skills_clean"] = df["skill_tags"].apply(normalize_skills)

    return df


def clean_cbnexus(df):

    df = df.copy()

    # Remove completely empty rows
    df = df.dropna(how="all")

    df["name_clean"] = df["Name"].apply(normalize_name)
    df["phone_clean"] = df["Phone Number"].apply(normalize_phone)
    df["city_clean"] = df["City"].apply(normalize_city)
    df["verified_clean"] = df["Verified"].apply(normalize_verified)

    return df


if __name__ == "__main__":

    naukri, gig_workers, cbnexus = load_sources()

    naukri = clean_naukri(naukri)
    gig_workers = clean_gig_workers(gig_workers)
    cbnexus = clean_cbnexus(cbnexus)

    print("Naukri rows:", len(naukri))
    print("Gig worker rows:", len(gig_workers))
    print("CBNexus rows:", len(cbnexus))

    print("\nSample normalized Naukri data:")
    print(
        naukri[
            ["name_clean", "email_clean", "phone_clean", "city_clean"]
        ].head()
    )

    print("\nSample normalized Gig Worker data:")
    print(
        gig_workers[
            ["name_clean", "email_clean", "city_clean", "status_clean"]
        ].head()
    )

    print("\nSample normalized CBNexus data:")
    print(
        cbnexus[
            ["name_clean", "phone_clean", "city_clean", "verified_clean"]
        ].head()
    )