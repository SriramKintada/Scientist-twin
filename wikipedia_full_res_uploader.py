"""
Fetch full-resolution scientist images from Wikipedia API
Uses imageinfo prop to get actual file URLs instead of thumbnails
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


def get_wikipedia_full_image(name: str):
    """Get full-resolution image URL from Wikipedia using imageinfo"""
    api_url = "https://en.wikipedia.org/w/api.php"

    # First get the page and image filename
    params = {
        "action": "query",
        "titles": name,
        "prop": "pageimages",
        "format": "json"
    }

    try:
        response = requests.get(api_url, params=params, headers=HEADERS, timeout=10)
        data = response.json()

        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if page_id != "-1":
                # Get the image title/filename
                image_title = page_data.get("pageimage", None)
                if not image_title:
                    return None

                # Now get the full image URL using imageinfo
                image_params = {
                    "action": "query",
                    "titles": f"File:{image_title}",
                    "prop": "imageinfo",
                    "iiprop": "url",
                    "format": "json"
                }

                img_response = requests.get(api_url, params=image_params, headers=HEADERS, timeout=10)
                img_data = img_response.json()

                img_pages = img_data.get("query", {}).get("pages", {})
                for img_page_id, img_page_data in img_pages.items():
                    if img_page_id != "-1":
                        imageinfo = img_page_data.get("imageinfo", [])
                        if imageinfo and len(imageinfo) > 0:
                            full_url = imageinfo[0].get("url", None)
                            return full_url

    except Exception as e:
        print(f"    Error: {e}")

    return None


def download_and_upload_image(image_url: str, scientist_name: str) -> str:
    """Download image and upload to Supabase"""
    if not image_url:
        return None

    try:
        # Download
        response = requests.get(image_url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
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
        return None


# Load scientists
with open('scientist_db_rich.json', 'r', encoding='utf-8') as f:
    scientists = json.load(f)

# Get scientists without images
missing_images = [s for s in scientists if not s.get('image_url')]

print("=" * 70)
print(f"WIKIPEDIA FULL-RESOLUTION IMAGE UPLOADER")
print("=" * 70)
print(f"Scientists missing images: {len(missing_images)}")
print()

updated = 0
failed = []
skipped = 0

for scientist in missing_images[:30]:  # Process first 30
    name = scientist['name']
    print(f"\n{name}")

    # Get full-res image URL
    print(f"  Fetching from Wikipedia...", end=" ")
    image_url = get_wikipedia_full_image(name)

    if not image_url:
        print("FAILED - No image found")
        failed.append(name)
        continue

    print(f"OK")
    print(f"  Downloading...", end=" ")

    # Upload to Supabase
    supabase_url = download_and_upload_image(image_url, name)

    if supabase_url:
        scientist['image_url'] = supabase_url
        updated += 1
        print("OK - Uploaded")
    else:
        failed.append(name)
        print("FAILED - Upload error")

    time.sleep(0.5)  # Rate limiting

# Save updated database
with open('scientist_db_rich.json', 'w', encoding='utf-8') as f:
    json.dump(scientists, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 70)
print(f"Updated: {updated} scientists")
print(f"Failed: {len(failed)}")
if failed:
    print(f"Failed scientists: {', '.join(failed[:10])}")
print("=" * 70)

# Count total with images
with_images = sum(1 for s in scientists if s.get('image_url'))
total = len(scientists)
print(f"\nTotal scientists: {total}")
print(f"With images: {with_images} ({with_images*100//total}%)")
print(f"Missing images: {total - with_images}")
