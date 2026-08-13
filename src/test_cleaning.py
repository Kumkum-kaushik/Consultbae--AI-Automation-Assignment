from cleaning import (
    normalize_name,
    normalize_email,
    normalize_phone,
    normalize_city,
    normalize_status,
    normalize_verified,
)


print("NAME:")
print(normalize_name("  ISHA   CHOPRA  "))

print("\nEMAIL:")
print(normalize_email(" ISHA.CHOPRA95@MAILTEST.EXAMPLE.ORG "))

print("\nPHONE:")
print(normalize_phone("+91-9000000131"))
print(normalize_phone("919000000131"))
print(normalize_phone("9000000131"))

print("\nCITY:")
print(normalize_city("GURGAON"))
print(normalize_city("Bangalore"))

print("\nSTATUS:")
print(normalize_status("ACTIVE"))

print("\nVERIFIED:")
print(normalize_verified("Y"))
print(normalize_verified("No"))