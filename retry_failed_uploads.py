"""
Retry failed image uploads with better rate limiting
"""

import json
import os
import requests
import time
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = "scientist-images"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
HEADERS = {'User-Agent': 'ScientistTwin/1.0 (contact@scirio.in)'}

# Failed scientists from previous run
FAILED_SCIENTISTS = [
    "K. VijayRaghavan",
    "V. S. Varadarajan",
    "R. Balasubramanian",
    "S. Chandrasekhar",
    "Ramamurti Rajaraman",
    "T. Ramasami",
    "P. Balaram",
    "Indira Nath",
    "Shafi Goldwasser",
    "Vidita Vaidya",
    "Bhaskara II",
    "K. Radhakrishnan"
]


def download_and_upload_image(image_url: str, scientist_name: str) -> str:
    """Download image and upload to Supabase with retries"""
    if not image_url or image_url == "null":
        return None

    # Try up to 3 times with exponential backoff
    for attempt in range(3):
        try:
            # Download with longer timeout
            response = requests.get(image_url, headers=HEADERS, timeout=30)
            if response.status_code != 200:
                if response.status_code == 429:
                    # Rate limited, wait longer
                    wait_time = (attempt + 1) * 5
                    print(f" Rate limited, waiting {wait_time}s...", end=" ")
                    time.sleep(wait_time)
                    continue
                print(f" Download failed: {response.status_code}")
                return None

            image_bytes = response.content

            # Create safe filename
            safe_name = scientist_name.lower().replace(" ", "_").replace(".", "").replace(",", "").replace("'", "")
            filename = f"{safe_name}.jpg"

            # Upload to Supabase
            supabase.storage.from_(BUCKET_NAME).upload(
                filename,
                image_bytes,
                {"content-type": "image/jpeg", "upsert": "true"}
            )

            public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(filename)
            return public_url

        except Exception as e:
            # If already exists, get URL anyway
            if "Duplicate" in str(e) or "already exists" in str(e):
                safe_name = scientist_name.lower().replace(" ", "_").replace(".", "").replace(",", "").replace("'", "")
                filename = f"{safe_name}.jpg"
                return supabase.storage.from_(BUCKET_NAME).get_public_url(filename)

            if attempt < 2:
                print(f" Error (attempt {attempt+1}), retrying...", end=" ")
                time.sleep(2)
            else:
                print(f" Error: {e}")
                return None

    return None


# Load image URLs mapping
with open('og_image_mapping.json', 'r', encoding='utf-8') as f:
    IMAGE_URLS = json.load(f)

# Load scientists database
with open('scientist_db_rich.json', 'r', encoding='utf-8') as f:
    scientists = json.load(f)

print("=" * 70)
print("RETRY FAILED UPLOADS WITH RATE LIMITING")
print("=" * 70)
print(f"Scientists to retry: {len(FAILED_SCIENTISTS)}")
print()

updated = 0
failed = []

for name in FAILED_SCIENTISTS:
    if name not in IMAGE_URLS:
        print(f"{name} - No URL in mapping, skipping")
        continue

    print(f"{name}")
    print(f"  Downloading & uploading...", end=" ")

    image_url = IMAGE_URLS[name]
    supabase_url = download_and_upload_image(image_url, name)

    if supabase_url:
        # Find and update scientist
        for scientist in scientists:
            if scientist['name'] == name:
                scientist['image_url'] = supabase_url
                updated += 1
                print("OK")
                break
    else:
        failed.append(name)
        print("FAILED")

    # Longer delay between requests to avoid rate limiting
    time.sleep(2)

# Save updated database
if updated > 0:
    with open('scientist_db_rich.json', 'w', encoding='utf-8') as f:
        json.dump(scientists, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 70)
print(f"Updated: {updated} scientists")
print(f"Failed: {len(failed)}")
if failed:
    print(f"Still failed: {', '.join(failed)}")
print("=" * 70)

# Count total with images
with_images = sum(1 for s in scientists if s.get('image_url'))
total = len(scientists)
print(f"\nTotal scientists: {total}")
print(f"With images: {with_images} ({with_images*100//total}%)")
print(f"Missing images: {total - with_images}")
