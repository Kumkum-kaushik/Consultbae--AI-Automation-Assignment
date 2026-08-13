from prepare_data import load_sources
from prepare_data import (
    clean_naukri,
    clean_gig_workers,
    clean_cbnexus
)

from matching import find_matches


def print_matches(
    source_name,
    target_name,
    source_df,
    target_df,
    matches
):

    print("\n" + "=" * 80)
    print(f"{source_name} <-> {target_name}")
    print("=" * 80)

    if not matches:
        print("No confident matches found.")
        return

    for match in matches:

        source = source_df.loc[match["source_index"]]
        target = target_df.loc[match["target_index"]]

        print("\n----------------------------------------")

        print(f"Match method: {match['method']}")

        print(
            f"{source_name}: "
            f"{source.get('name_clean')} | "
            f"Email: {source.get('email_clean')} | "
            f"Phone: {source.get('phone_clean')} | "
            f"City: {source.get('city_clean')}"
        )

        print(
            f"{target_name}: "
            f"{target.get('name_clean')} | "
            f"Email: {target.get('email_clean')} | "
            f"Phone: {target.get('phone_clean')} | "
            f"City: {target.get('city_clean')}"
        )


if __name__ == "__main__":

    # Load raw data
    naukri, gig_workers, cbnexus = load_sources()

    # Clean data
    naukri = clean_naukri(naukri)
    gig_workers = clean_gig_workers(gig_workers)
    cbnexus = clean_cbnexus(cbnexus)

    # Compare Naukri with Gig Workers
    naukri_gig_matches = find_matches(
        naukri,
        gig_workers
    )

    # Compare Naukri with CBNexus
    naukri_cbnexus_matches = find_matches(
        naukri,
        cbnexus
    )

    # Compare Gig Workers with CBNexus
    gig_cbnexus_matches = find_matches(
        gig_workers,
        cbnexus
    )

    print_matches(
        "Naukri",
        "Gig Workers",
        naukri,
        gig_workers,
        naukri_gig_matches
    )
    print_matches(
        "Naukri",
        "CBNexus",
        naukri,
        cbnexus,
        naukri_cbnexus_matches
    )

    print_matches(
        "Gig Workers",
        "CBNexus",
        gig_workers,
        cbnexus,
        gig_cbnexus_matches
    )