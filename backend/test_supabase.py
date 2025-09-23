import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

print(f"URL: {supabase_url}")
print(f"Key: {supabase_key[:10]}...{supabase_key[-10:]}")

try:
    supabase = create_client(supabase_url, supabase_key)
    
    # Test a simple query
    response = supabase.table("documents").select("*").limit(1).execute()
    print("Connection successful!")
    print(f"Response: {response}")
except Exception as e:
    print(f"Error: {str(e)}")