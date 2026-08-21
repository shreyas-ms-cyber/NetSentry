"""
One-time script to add alert_type column to alerts table
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

def add_alert_type_column():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set")
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        # Check if column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='alerts' AND column_name='alert_type'
        """)
        
        if cur.fetchone():
            print("✅ alert_type column already exists")
            cur.close()
            conn.close()
            return True
        
        # Add the column
        print("📝 Adding alert_type column...")
        cur.execute("""
            ALTER TABLE alerts ADD COLUMN alert_type VARCHAR(50) NOT NULL DEFAULT 'NEW_DEVICE'
        """)
        conn.commit()
        print("✅ alert_type column added successfully")
        
        # Update existing rows with default value if any
        cur.execute("""
            UPDATE alerts SET alert_type = 'NEW_DEVICE' WHERE alert_type IS NULL
        """)
        conn.commit()
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = add_alert_type_column()
    sys.exit(0 if success else 1)
