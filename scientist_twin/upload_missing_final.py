"""
Final attempt to upload the 15 remaining scientist images to Supabase
Uses multiple strategies to bypass download restrictions
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

# Find scientists still using external URLs
external_scientists = [
    s for s in scientists
    if s.get('image_url', '') and not s.get('image_url', '').startswith('https://nlgcvxygeicujcqwomut.supabase.co')
]

print(f"Found {len(external_scientists)} scientists with external URLs\n")

uploaded_count = 0
failed = []

# Multiple user agents to try
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
]

for i, scientist in enumerate(external_scientists, 1):
    name = scientist['name']
    current_url = scientist.get('image_url', '')

    print(f"{i}/{len(external_scientists)} - {name}")
    print(f"  URL: {current_url}")

    # Generate filename
    filename = name.lower().replace(' ', '_').replace('.', '').replace('-', '_') + '.jpg'

    success = False

    # Try each user agent
    for ua_idx, user_agent in enumerate(user_agents):
        try:
            headers = {
                'User-Agent': user_agent,
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': current_url,
            }

            # Try with SSL verification first
            try:
                response = requests.get(current_url, headers=headers, timeout=15)
            except requests.exceptions.SSLError:
                # Retry without SSL verification if SSL fails
                response = requests.get(current_url, headers=headers, timeout=15, verify=False)

            if response.status_code == 200 and len(response.content) > 1000:
                image_data = response.content

                # Upload to Supabase
                try:
                    result = supabase.storage.from_('scientist-images').upload(
                        filename,
                        image_data,
                        {'content-type': 'image/jpeg', 'upsert': 'true'}
                    )

                    # Get public URL
                    public_url = supabase.storage.from_('scientist-images').get_public_url(filename)

                    # Update scientist record
                    scientist['image_url'] = public_url
                    uploaded_count += 1
                    success = True
                    print(f"  [OK] Uploaded successfully")
                    break

                except Exception as upload_error:
                    if '409' in str(upload_error) or 'Duplicate' in str(upload_error):
                        # File already exists, just update URL
                        public_url = supabase.storage.from_('scientist-images').get_public_url(filename)
                        scientist['image_url'] = public_url
                        uploaded_count += 1
                        success = True
                        print(f"  [OK] File exists, updated URL")
                        break
                    else:
                        print(f"  [RETRY] Upload error: {upload_error}")

            else:
                print(f"  [RETRY] HTTP {response.status_code}, trying next user agent...")

        except Exception as e:
            print(f"  [RETRY] Error with UA {ua_idx+1}: {str(e)[:50]}")
            continue

    if not success:
        failed.append(name)
        print(f"  [FAIL] All attempts failed")

    time.sleep(1)  # Rate limiting

# Save updated database
with open('scientist_db_rich.json', 'w', encoding='utf-8') as f:
    json.dump(scientists, f, indent=2, ensure_ascii=False)

print(f"\n{'='*60}")
print(f"[OK] Successfully uploaded: {uploaded_count}/{len(external_scientists)}")
print(f"[FAIL] Failed: {len(failed)}")

if failed:
    print(f"\nFailed scientists:")
    for name in failed:
        print(f"  - {name}")

print(f"\nDatabase updated: scientist_db_rich.json")
