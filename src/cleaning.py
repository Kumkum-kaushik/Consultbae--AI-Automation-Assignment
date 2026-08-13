import re
import pandas as pd


def clean_text(value):
    """Clean a general text field."""
    if pd.isna(value):
        return None

    value = str(value).strip()

    if not value:
        return None

    return value


def normalize_name(value):
    """Normalize a person's name for matching."""
    value = clean_text(value)

    if value is None:
        return None

    value = value.lower()
    value = re.sub(r"\s+", " ", value)

    return value


def normalize_email(value):
    """Normalize email for matching."""
    value = clean_text(value)

    if value is None:
        return None

    return value.lower()


def normalize_phone(value):
    """
    Normalize Indian phone numbers.

    Examples:
    +91-9000000131 -> 9000000131
    919000000131  -> 9000000131
    9000000131    -> 9000000131
    """

    value = clean_text(value)

    if value is None:
        return None

    digits = re.sub(r"\D", "", value)

    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]

    if len(digits) == 10:
        return digits

    return digits


def normalize_city(value):
    """Normalize city names for matching."""
    value = clean_text(value)

    if value is None:
        return None

    value = value.lower()

    city_mapping = {
        "gurgaon": "gurugram",
        "gurugram": "gurugram",
        "bangalore": "bengaluru",
        "bengaluru": "bengaluru",
        "new delhi": "new delhi",
        "delhi": "delhi",
        "delhi ncr": "delhi ncr",
        "noida": "noida",
        "pune": "pune",
    }

    return city_mapping.get(value, value)


def normalize_status(value):
    """Normalize worker status."""
    value = clean_text(value)

    if value is None:
        return None

    return value.lower()


def normalize_verified(value):
    """Normalize verification values to yes/no."""
    value = clean_text(value)

    if value is None:
        return None

    value = value.lower()

    if value in ["y", "yes"]:
        return "yes"

    if value in ["n", "no"]:
        return "no"

    return value


def normalize_skills(value):
    """Normalize skill tags while preserving the list."""
    value = clean_text(value)

    if value is None:
        return None

    skills = [
        skill.strip().lower()
        for skill in value.split(",")
        if skill.strip()
    ]

    return ", ".join(skills)