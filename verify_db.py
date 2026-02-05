import sqlite3

conn = sqlite3.connect('db/cloud.db')

# Check tables
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Tables created:", [t[0] for t in tables])

# Check users count
users_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
print(f"Users in database: {users_count}")

if users_count == 0:
    print("\nNo users found. Creating default admin user...")
    conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                 ('admin', 'admin123', 'admin'))
    conn.commit()
    print("Default admin user created!")
    print("  Username: admin")
    print("  Password: admin123")
    print("  Role: admin")

conn.close()
