import sqlite3
import os

DB_PATH = os.path.join('db', 'cloud.db')

def reset_password():
    """Reset password for an existing user"""
    print("=" * 60)
    print("Password Reset Tool")
    print("=" * 60)
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Show existing users
    print("\nExisting users:")
    users = conn.execute("SELECT id, username, role FROM users").fetchall()
    for user in users:
        print(f"  [{user['id']}] {user['username']} ({user['role']})")
    
    print("\n" + "=" * 60)
    
    # Get user input
    username = input("Enter username to reset password: ").strip()
    
    # Check if user exists
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    
    if not user:
        print(f"\n[ERROR] User '{username}' not found!")
        conn.close()
        return
    
    # Get new password
    new_password = input(f"Enter new password for '{username}': ").strip()
    
    if not new_password:
        print("\n[ERROR] Password cannot be empty!")
        conn.close()
        return
    
    # Update password
    conn.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print(f"[SUCCESS] Password updated successfully!")
    print(f"   Username: {username}")
    print(f"   New Password: {new_password}")
    print("=" * 60)
    print("\nYou can now log in with these credentials.")

if __name__ == "__main__":
    try:
        reset_password()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n[ERROR] {e}")
