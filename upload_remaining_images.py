"""
Upload remaining scientist images to Supabase storage
Identifies scientists without Supabase-hosted images and uploads them
"""

from supabase import create_client
from dotenv import load_dotenv
import os
import json
import requests
from urllib.parse import quote
import time

load_dotenv()

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Load database
with open('scientist_db_rich.json', encoding='utf-8') as f:
    scientists = json.load(f)

# Find scientists NOT using Supabase storage
missing_supabase = []
for s in scientists:
    url = s.get('image_url', '')
    if not url.startswith('https://nlgcvxygeicujcqwomut.supabase.co'):
        missing_supabase.append(s)

print(f"Found {len(missing_supabase)} scientists without Supabase-hosted images\n")

uploaded_count = 0
failed = []

for i, scientist in enumerate(missing_supabase, 1):
    name = scientist['name']
    current_url = scientist.get('image_url', '')

    print(f"{i}/{len(missing_supabase)} - {name}")
    print(f"  Current URL: {current_url[:80]}...")

    # Generate filename
    filename = name.lower().replace(' ', '_').replace('.', '') + '.jpg'

    try:
        # Download image
        if current_url:
            response = requests.get(current_url, timeout=10)
            if response.status_code == 200:
                image_data = response.content

                # Upload to Supabase
                result = supabase.storage.from_('scientist-images').upload(
                    filename,
                    image_data,
                    {'content-type': 'image/jpeg'}
                )

                # Get public URL
                public_url = supabase.storage.from_('scientist-images').get_public_url(filename)

                # Update scientist record
                scientist['image_url'] = public_url
                uploaded_count += 1
                print(f"  [OK] Uploaded: {filename}")
            else:
                print(f"  [FAIL] Failed to download: HTTP {response.status_code}")
                failed.append(name)
        else:
            print(f"  [SKIP] No image URL available")
            failed.append(name)

    except Exception as e:
        print(f"  [ERROR] {e}")
        failed.append(name)

    time.sleep(0.5)  # Rate limiting

# Save updated database
with open('scientist_db_rich.json', 'w', encoding='utf-8') as f:
    json.dump(scientists, f, indent=2, ensure_ascii=False)

print(f"\n{'='*60}")
print(f"[OK] Successfully uploaded: {uploaded_count}/{len(missing_supabase)}")
print(f"[FAIL] Failed: {len(failed)}")

if failed:
    print(f"\nFailed scientists:")
    for name in failed:
        print(f"  - {name}")

print(f"\nDatabase updated: scientist_db_rich.json")
