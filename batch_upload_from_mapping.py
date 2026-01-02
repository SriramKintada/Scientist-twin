"""
Batch upload scientist images to Supabase from og_image_mapping.json
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


def download_and_upload_image(image_url: str, scientist_name: str) -> str:
    """Download image and upload to Supabase"""
    if not image_url or image_url == "null":
        return None

    try:
        # Download
        response = requests.get(image_url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"    Download failed: {response.status_code}")
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
        print(f"    Error: {e}")
        return None


# Load image URLs mapping
with open('og_image_mapping.json', 'r', encoding='utf-8') as f:
    IMAGE_URLS = json.load(f)

# Load scientists database
with open('scientist_db_rich.json', 'r', encoding='utf-8') as f:
    scientists = json.load(f)

print("=" * 70)
print("BATCH IMAGE UPLOADER FROM OG:IMAGE MAPPING")
print("=" * 70)
print(f"Images to upload: {len(IMAGE_URLS)}")
print()

updated = 0
failed = []

for scientist in scientists:
    name = scientist['name']

    # Skip if already has image
    if scientist.get('image_url'):
        continue

    # Check if we have URL for this scientist
    if name not in IMAGE_URLS:
        continue

    image_url = IMAGE_URLS[name]
    print(f"{name}")
    print(f"  Downloading & uploading...", end=" ")

    supabase_url = download_and_upload_image(image_url, name)

    if supabase_url:
        scientist['image_url'] = supabase_url
        updated += 1
        print("OK")
    else:
        failed.append(name)
        print("FAILED")

    time.sleep(0.3)

# Save updated database
if updated > 0:
    with open('scientist_db_rich.json', 'w', encoding='utf-8') as f:
        json.dump(scientists, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 70)
print(f"Updated: {updated} scientists")
print(f"Failed: {len(failed)}")
if failed:
    print(f"Failed scientists: {', '.join(failed[:10])}")
    if len(failed) > 10:
        print(f"  ... and {len(failed)-10} more")
print("=" * 70)

# Count total with images
with_images = sum(1 for s in scientists if s.get('image_url'))
total = len(scientists)
print(f"\nTotal scientists: {total}")
print(f"With images: {with_images} ({with_images*100//total}%)")
print(f"Missing images: {total - with_images}")
