import pandas as pd
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data"


def inspect_file(filename):

    path = DATA_DIR / filename
    df = pd.read_csv(path)

    print("\n" + "=" * 70)
    print(filename)
    print("=" * 70)

    # Missing values
    print("\n1. Missing values")
    print(df.isnull().sum())

    # Duplicate rows
    print("\n2. Duplicate complete rows")
    print(df.duplicated().sum())

    # Column information
    print("\n3. Data types")
    print(df.dtypes)

    return df


if __name__ == "__main__":

    files = [
        "source1_naukri_applicants.csv",
        "source2_gig_workers.csv",
        "source3_cbnexus_contacts.csv"
    ]

    for file in files:
        inspect_file(file)