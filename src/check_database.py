import sqlite3


conn = sqlite3.connect("consultbae.db")

cursor = conn.cursor()

cursor.execute("""
    SELECT
        person_id,
        name,
        email,
        phone,
        city,
        source_records
    FROM people
    ORDER BY person_id
""")

rows = cursor.fetchall()

print("\nTotal people:", len(rows))

print("\nPeople:")
print("-" * 100)

for row in rows:
    print(row)

conn.close()