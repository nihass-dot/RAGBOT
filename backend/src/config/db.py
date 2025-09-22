# src/config/db.py
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

supabase_url: str = os.environ.get("SUPABASE_URL")
supabase_key: str = os.environ.get("SUPABASE_KEY")

# Create the supabase client
supabase: Client = create_client(supabase_url, supabase_key)

# Export the supabase client
__all__ = ['supabase']