import os
import sys

# Ensure backend package is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_supabase_sdk():
    from supabase import create_client
    url = "https://igdmmemenujwnwxpfvtq.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlnZG1tZW1lbnVqd253eHBmdnRxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODUxNTQ1MzYsImV4cCI6MjEwMDczMDUzNn0.dzmBquS5kCgVk-ndW1Yw2gB6CkeUDDbpd7GPu_004Ig"
    
    print("Testing Supabase SDK Client connection via HTTPS (port 443)...")
    try:
        client = create_client(url, key)
        # Query the users table (even if it's empty or doesn't exist yet, a response confirms API connectivity)
        response = client.table("users").select("*").limit(1).execute()
        print("Success! SDK connection established.")
        print(f"Response: {response}")
    except Exception as e:
        print(f"SDK Connection Failed: {e}")

if __name__ == "__main__":
    test_supabase_sdk()
