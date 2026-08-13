from matching import exact_match


person_a = {
    "name_clean": "isha chopra",
    "email_clean": "isha.chopra95@mailtest.example.org",
    "phone_clean": "9000000138",
    "city_clean": "pune"
}


person_b = {
    "name_clean": "isha chopra",
    "email_clean": "isha.chopra95@mailtest.example.org",
    "phone_clean": None,
    "city_clean": "pune"
}


person_c = {
    "name_clean": "isha chopra",
    "email_clean": None,
    "phone_clean": "9000000138",
    "city_clean": "pune"
}


person_d = {
    "name_clean": "isha chopra",
    "email_clean": "different@email.com",
    "phone_clean": "9000000999",
    "city_clean": "delhi"
}


print("A vs B:", exact_match(person_a, person_b))
print("A vs C:", exact_match(person_a, person_c))
print("A vs D:", exact_match(person_a, person_d))