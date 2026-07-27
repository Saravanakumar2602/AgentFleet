import os
import sys

# Ensure backend package is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from sqlalchemy import text
from backend.app.database.supabase import SessionLocal

def migrate():
    db = SessionLocal()
    print("Altering 'chk_trips_status' constraint in Supabase database...")
    try:
        # Drop the existing check constraint
        db.execute(text("ALTER TABLE trips DROP CONSTRAINT IF EXISTS chk_trips_status"))
        
        # Add the new check constraint supporting 'Route Generated'
        db.execute(text("""
            ALTER TABLE trips 
            ADD CONSTRAINT chk_trips_status 
            CHECK (status IN ('Pending', 'Assigned', 'In Transit', 'Route Generated', 'Completed', 'Cancelled'))
        """))
        db.commit()
        print("Constraint migration successful!")
    except Exception as e:
        db.rollback()
        print(f"Migration failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
