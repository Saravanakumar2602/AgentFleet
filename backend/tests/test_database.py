import os
import sys

# Ensure backend package is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.database.supabase import health_check

def main():
    print("Attempting to connect to the database...")
    try:
        # Executes health_check which runs 'SELECT 1'
        if health_check():
            print("Connection Successful")
            sys.exit(0)
        else:
            print("Connection Failed: Unknown error")
            sys.exit(1)
    except Exception as e:
        print(f"Connection Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
