"""
Check actual Supabase scientists table schema
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Fetching sample scientist from Supabase...")
try:
    result = supabase.table('scientists').select('*').limit(1).execute()

    if result.data:
        scientist = result.data[0]
        print("\n Columns in Supabase scientists table:")
        print("="*60)
        for key in sorted(scientist.keys()):
            print(f"  - {key}: {type(scientist[key]).__name__}")
        print("="*60)
        print(f"\nTotal columns: {len(scientist.keys())}")
    else:
        print("No scientists found in database")
except Exception as e:
    print(f"Error: {e}")
