import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

supabase_url: str = os.environ.get("SUPABASE_URL")
supabase_key: str = os.environ.get("SUPABASE_KEY")

# Add validation for environment variables
if not supabase_url:
    raise ValueError("SUPABASE_URL must be set in environment variables")
if not supabase_key:
    raise ValueError("SUPABASE_KEY must be set in environment variables")

print(f"Supabase URL: {supabase_url}")
print(f"Supabase Key: {supabase_key[:10]}...{supabase_key[-10:]}")

# Create the supabase client
try:
    supabase: Client = create_client(supabase_url, supabase_key)
    print("Supabase client created successfully")
except Exception as e:
    print(f"Error creating Supabase client: {str(e)}")
    raise

# Export the supabase client
__all__ = ['supabase']