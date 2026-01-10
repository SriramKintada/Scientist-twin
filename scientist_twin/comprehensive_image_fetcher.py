"""
Comprehensive image fetcher - tries multiple methods to get 100% coverage
1. Wikipedia API (pageimages + imageinfo)
2. Wikimedia Commons direct URLs
3. Manual mapping for known scientists
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

# Manually extracted og:image URLs from Playwright
KNOWN_OG_IMAGES = {'K. S. Krishnan': 'https://upload.wikimedia.org/wikipedia/commons/9/9f/Kariamanickam_Srinivasa_Krishnan_1952_London.jpg', 'G. N. Ramachandran': 'https://upload.wikimedia.org/wikipedia/en/5/59/G_N_Ramachandran.jpg', 'Raja Ramanna': 'https://upload.wikimedia.org/wikipedia/en/0/00/RajaRamannaPic.jpg'}


def get_wikipedia_image_wikidata(name: str):
    """Try to get image from Wikidata/Wikipedia using multiple methods"""
    # Try Wikipedia API with proper query
    api_url = "https://en.wikipedia.org/w/api.php"

    # Method 1: Get page info with original image
    params = {
        "action": "query",
        "titles": name,
        "prop": "pageimages|pageterms",
        "piprop": "original",
        "format": "json"
    }

    try:
        response = requests.get(api_url, params=params, headers=HEADERS, timeout=10)
        data = response.json()

        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if page_id != "-1":
                # Check for original image
                original = page_data.get("original", {})
                if original and "source" in original:
                    return original["source"]

                # Check for pageimage
                pageimage = page_data.get("pageimage")
                if pageimage:
                    # Get full image info
                    img_params = {
                        "action": "query",
                        "titles": f"File:{pageimage}",
                        "prop": "imageinfo",
                        "iiprop": "url",
                        "format": "json"
                    }

                    img_response = requests.get(api_url, params=img_params, headers=HEADERS, timeout=10)
                    img_data = img_response.json()

                    img_pages = img_data.get("query", {}).get("pages", {})
                    for img_page_id, img_page_data in img_pages.items():
                        if img_page_id != "-1":
                            imageinfo = img_page_data.get("imageinfo", [])
                            if imageinfo and len(imageinfo) > 0:
                                return imageinfo[0].get("url")
    except Exception as e:
        print(f"    API Error: {e}")

    return None


def download_and_upload_image(image_url: str, scientist_name: str) -> str:
    """Download image and upload to Supabase"""
    if not image_url or image_url == "null":
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


# Load scientists database
with open('scientist_db_rich.json', 'r', encoding='utf-8') as f:
    scientists = json.load(f)

# Get scientists without images
missing = [s for s in scientists if not s.get('image_url')]

print("=" * 70)
print("COMPREHENSIVE IMAGE FETCHER - MULTI-METHOD APPROACH")
print("=" * 70)
print(f"Scientists missing images: {len(missing)}")
print()

updated = 0
failed = []

for scientist in missing:
    name = scientist['name']
    print(f"\n{name}")

    image_url = None

    # Strategy 1: Check manual mapping first
    if name in KNOWN_OG_IMAGES:
        print(f"  Using known URL...", end=" ")
        image_url = KNOWN_OG_IMAGES[name]
        print("Found")

    # Strategy 2: Try Wikipedia API
    if not image_url:
        print(f"  Trying Wikipedia API...", end=" ")
        image_url = get_wikipedia_image_wikidata(name)
        if image_url:
            print("Found")
        else:
            print("Not found")

    # Upload if we found an image
    if image_url:
        print(f"  Uploading...", end=" ")
        supabase_url = download_and_upload_image(image_url, name)

        if supabase_url:
            scientist['image_url'] = supabase_url
            updated += 1
            print("OK")
        else:
            failed.append(name)
            print("FAILED")
    else:
        print(f"  SKIP - No image source found")
        failed.append(name)

    time.sleep(0.5)

# Save updated database
if updated > 0:
    with open('scientist_db_rich.json', 'w', encoding='utf-8') as f:
        json.dump(scientists, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 70)
print(f"Updated: {updated} scientists")
print(f"Failed: {len(failed)}")
if failed:
    print(f"\nScientists still missing images:")
    for name in failed[:20]:
        print(f"  - {name}")
    if len(failed) > 20:
        print(f"  ... and {len(failed)-20} more")
print("=" * 70)

# Count total with images
with_images = sum(1 for s in scientists if s.get('image_url'))
total = len(scientists)
print(f"\nTotal scientists: {total}")
print(f"With images: {with_images} ({with_images*100//total}%)")
print(f"Missing images: {total - with_images}")
