import sqlite3

# Connect to the SQLite database (create a new one if it doesn't exist)
conn = sqlite3.connect('partnerdb.sqlite')
cursor = conn.cursor()

# Drop existing tables if they exist
cursor.execute("DROP TABLE IF EXISTS partners")

# Create a new table for partners
cursor.execute("""
    CREATE TABLE partners (
        id INTEGER PRIMARY KEY,
        name TEXT,
        role TEXT,
        service_type TEXT,
        available_days TEXT,
        contact_email TEXT,
        contact_phone TEXT
    )
""")

# Insert sample data into the partners table
sample_partners = [
    ('Red Cross', 'Volunteer Coordinator', 'Disaster Relief', 'Monday, Wednesday, Friday', 'volunteer@redcross.org', '123-456-7890'),
    ('Feeding America', 'Food Distribution Manager', 'Food Assistance', 'Tuesday, Thursday', 'food@feedingamerica.org', '987-654-3210'),
    ('Habitat for Humanity', 'Construction Supervisor', 'Housing Support', 'Monday, Wednesday, Friday', 'construction@habitat.org', '111-222-3333'),
    ('UNICEF', 'Program Manager', 'Child Welfare', 'Monday, Tuesday, Thursday', 'program@unicef.org', '444-555-6666'),
    ('Doctors Without Borders', 'Volunteer', 'Medical Aid', 'Monday, Wednesday, Friday', 'volunteer@doctors.org', '777-888-9999'),
    ('American Red Cross', 'Volunteer', 'Emergency Response', 'Tuesday, Thursday', 'volunteer@redcross.org', '555-444-3333'),
    ('Salvation Army', 'Volunteer', 'Social Services', 'Monday, Tuesday, Thursday', 'volunteer@salvationarmy.org', '222-333-4444'),
    ('Habitat for Humanity', 'Volunteer', 'Home Construction', 'Monday, Wednesday, Friday', 'volunteer@habitat.org', '999-888-7777'),
    ('UNICEF', 'Volunteer', 'Child Advocacy', 'Tuesday, Thursday', 'volunteer@unicef.org', '666-777-8888'),
    ('Feeding America', 'Volunteer', 'Food Bank', 'Monday, Wednesday, Friday', 'volunteer@feedingamerica.org', '333-222-1111'),
]

cursor.executemany("INSERT INTO partners (name, role, service_type, available_days, contact_email, contact_phone) VALUES (?, ?, ?, ?, ?, ?)", sample_partners)

# Commit changes and close the connection
conn.commit()
conn.close()

print("Sample data inserted successfully into partnerdb.sqlite")
