"""
Migration: Add is_diagnostic_in_progress column to users table.
Security Fix #2: Prevents concurrent diagnostic submissions.

Run with: python scripts/add_diagnostic_flag.py
"""

import sys
sys.path.insert(0, '.')

from database import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        # Check if column already exists
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name='users' AND column_name='is_diagnostic_in_progress'
        """))
        
        if result.fetchone():
            print("Column 'is_diagnostic_in_progress' already exists. Skipping.")
            return
        
        conn.execute(text("""
            ALTER TABLE users 
            ADD COLUMN is_diagnostic_in_progress BOOLEAN DEFAULT FALSE
        """))
        conn.commit()
        print("✅ Added 'is_diagnostic_in_progress' column to users table.")

if __name__ == "__main__":
    migrate()
