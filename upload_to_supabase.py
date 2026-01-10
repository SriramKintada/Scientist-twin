"""
Upload scientist database to Supabase
Reads scientist_db_rich.json and uploads all scientists to Supabase PostgreSQL
"""

import json
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load scientists from JSON
with open('scientist_db_rich.json', 'r', encoding='utf-8') as f:
    scientists = json.load(f)

print("=" * 70)
print("UPLOADING SCIENTIST DATABASE TO SUPABASE")
print("=" * 70)
print(f"Total scientists to upload: {len(scientists)}")
print(f"Scientists with images: {sum(1 for s in scientists if s.get('image_url'))}")
print()

# First, clear existing data
print("Clearing existing data...")
try:
    supabase.table('scientists').delete().neq('id', 0).execute()
    print("  Existing data cleared")
except Exception as e:
    print(f"  Note: {e}")

print()
print("Uploading scientists...")

uploaded = 0
errors = []

# Upload in batches of 50
batch_size = 50
for i in range(0, len(scientists), batch_size):
    batch = scientists[i:i+batch_size]

    # Prepare data for upload - ONLY include fields that exist in Supabase schema
    # Schema: name, field, subfield, traits, archetype, era, achievements, summary, moments, working_style, wiki_title, embedding
    upload_data = []
    for scientist in batch:
        record = {
            'name': scientist['name'],
            'field': scientist['field'],
            'subfield': scientist.get('subfield', ''),
            'traits': scientist['traits'],
            'archetype': scientist.get('archetype', 'Distinguished Researcher'),
            'era': scientist.get('era', 'Contemporary Leader'),
            'achievements': scientist.get('achievements', ''),
            'summary': scientist.get('summary', ''),
            'moments': scientist.get('moments', []),
            'working_style': scientist.get('working_style', ''),
            'wiki_title': scientist.get('wiki_title', scientist['name'])
        }
        upload_data.append(record)

    try:
        # Upsert batch (insert or update if exists)
        response = supabase.table('scientists').upsert(upload_data, on_conflict='name').execute()
        uploaded += len(batch)
        print(f"  Upserted batch {i//batch_size + 1}: {i+1}-{min(i+batch_size, len(scientists))}/{len(scientists)}")
    except Exception as e:
        print(f"  ERROR in batch {i//batch_size + 1}: {e}")
        errors.append(f"Batch {i//batch_size + 1}: {e}")

print()
print("=" * 70)
print("UPLOAD COMPLETE")
print("=" * 70)
print(f"Total uploaded: {uploaded}/{len(scientists)}")
print(f"Errors: {len(errors)}")

if errors:
    print("\nErrors encountered:")
    for error in errors[:5]:
        print(f"  - {error}")
    if len(errors) > 5:
        print(f"  ... and {len(errors)-5} more")

# Verify upload
print("\nVerifying upload...")
try:
    result = supabase.table('scientists').select('id', count='exact').execute()
    count = result.count if hasattr(result, 'count') else len(result.data)
    print(f"Scientists in database: {count}")

    # Note: Image URLs are stored in local JSON file, not in Supabase table
    print(f"Note: Image URLs managed separately in scientist_db_rich.json")
except Exception as e:
    print(f"Verification error: {e}")

print()
print("Database deployment to Supabase complete!")
