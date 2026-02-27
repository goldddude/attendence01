"""
Complete Database Migration Script
Adds ALL missing columns to attendance table
"""
import sqlite3
import os

# Get the database path - check both locations
db_paths = [
    os.path.join(os.path.dirname(__file__), 'instance', 'nfc_attendance.db'),
    os.path.join(os.path.dirname(__file__), 'nfc_attendance.db')
]

# Use the first one that exists
db_path = None
for path in db_paths:
    if os.path.exists(path):
        db_path = path
        break

if not db_path:
    print("[ERROR] Database file not found!")
    exit(1)

print(f"Connecting to database: {db_path}")

try:
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check current columns
    cursor.execute("PRAGMA table_info(attendance)")
    columns = [column[1] for column in cursor.fetchall()]
    
    print(f"\n[INFO] Current columns in attendance table:")
    for col in columns:
        print(f"   - {col}")
    
    # Define all required columns
    required_columns = {
        'section': 'VARCHAR(20)',
        'subject': 'VARCHAR(100)',
        'date': 'VARCHAR(20)',
        'class_time': 'VARCHAR(20)'
    }
    
    print(f"\n[CHECK] Checking for missing columns...")
    
    # Add missing columns
    added_count = 0
    for column_name, column_type in required_columns.items():
        if column_name not in columns:
            print(f"   Adding '{column_name}' column ({column_type})...")
            cursor.execute(f"ALTER TABLE attendance ADD COLUMN {column_name} {column_type}")
            added_count += 1
            print(f"   [SUCCESS] '{column_name}' column added successfully")
        else:
            print(f"   [INFO] '{column_name}' column already exists")
    
    # Commit changes
    if added_count > 0:
        conn.commit()
        print(f"\n[SUCCESS] Added {added_count} new column(s)")
    else:
        print(f"\n[SUCCESS] All columns already exist - no changes needed")
    
    # Create indexes for better performance
    print(f"\n[INDEX] Creating indexes...")
    
    indexes = [
        ('idx_attendance_section', 'section'),
        ('idx_attendance_subject', 'subject'),
        ('idx_attendance_date', 'date')
    ]
    
    for index_name, column_name in indexes:
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON attendance({column_name})")
            print(f"   [SUCCESS] Index '{index_name}' created")
        except Exception as e:
            print(f"   [INFO] Index '{index_name}' already exists or error: {e}")
    
    conn.commit()
    
    # Verify the final schema
    cursor.execute("PRAGMA table_info(attendance)")
    final_columns = [column[1] for column in cursor.fetchall()]
    
    print(f"\n[SUCCESS] FINAL SCHEMA - Attendance table columns:")
    for col in final_columns:
        print(f"   - {col}")
    
    print("\n[COMPLETE] Database migration completed successfully!")
    print("[SUCCESS] All required columns are now present")
    print("[SUCCESS] Indexes created for better performance")
    print("\n[ACTION] Please restart the server for changes to take effect")
    
except Exception as e:
    print(f"\n[ERROR] Error during migration: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
    
finally:
    conn.close()
    print("\nDatabase connection closed.")
