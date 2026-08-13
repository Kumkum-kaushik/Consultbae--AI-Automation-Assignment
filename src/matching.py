def exact_match(record1, record2):
    """
    Check whether two records clearly refer
    to the same person.

    Matching priority:
    1. Email
    2. Phone
    3. Name + City
    """

    # 1. Email match
    email1 = record1.get("email_clean")
    email2 = record2.get("email_clean")

    if email1 and email2 and email1 == email2:
        return True, "email"

    # 2. Phone match
    phone1 = record1.get("phone_clean")
    phone2 = record2.get("phone_clean")

    if phone1 and phone2 and phone1 == phone2:
        return True, "phone"

    # 3. Name + city match
    name1 = record1.get("name_clean")
    name2 = record2.get("name_clean")

    city1 = record1.get("city_clean")
    city2 = record2.get("city_clean")

    if (
        name1
        and name2
        and name1 == name2
        and city1
        and city2
        and city1 == city2
    ):
        return True, "name_city"

    return False, None


def find_matches(source_records, target_records):
    """
    Compare records from two sources
    and return all confident matches.
    """

    matches = []

    for source_index, source in source_records.iterrows():

        for target_index, target in target_records.iterrows():

            matched, method = exact_match(
                source.to_dict(),
                target.to_dict()
            )

            if matched:

                matches.append({
                    "source_index": source_index,
                    "target_index": target_index,
                    "method": method
                })

    return matches