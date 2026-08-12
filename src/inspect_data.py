import pandas as pd
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data"


files = [
    "source1_naukri_applicants.csv",
    "source2_gig_workers.csv",
    "source3_cbnexus_contacts.csv"
]


for file in files:
    path = DATA_DIR / file

    df = pd.read_csv(path)

    print("\n" + "=" * 60)
    print(file)
    print("=" * 60)

    print("Rows:", len(df))
    print("Columns:", list(df.columns))

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nFirst 5 rows:")
    print(df.head())