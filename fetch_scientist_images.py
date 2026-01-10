"""
Fetch scientist images from Wikipedia and upload to Supabase Storage
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

# Important: Add User-Agent header for Wikipedia
HEADERS = {'User-Agent': 'ScientistTwin/1.0 (contact@scirio.in)'}


def get_wikipedia_image_url(name: str, wiki_title: str = None) -> str:
    """Get the main image URL from Wikipedia for a person"""
    title = wiki_title or name.replace(" ", "_")

    api_url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "titles": title,
        "prop": "pageimages",
        "pithumbsize": 400,
        "format": "json"
    }

    try:
        response = requests.get(api_url, params=params, headers=HEADERS, timeout=10)
        data = response.json()

        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if page_id != "-1":
                thumbnail = page_data.get("thumbnail", {})
                if thumbnail.get("source"):
                    return thumbnail["source"]

    except Exception as e:
        print(f"    Error fetching Wikipedia image: {e}")

    return None


def download_image(url: str) -> bytes:
    """Download image from URL and return bytes"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        print(f"    Error downloading: {e}")
    return None


def upload_to_supabase(image_bytes: bytes, filename: str) -> str:
    """Upload image to Supabase storage and return public URL"""
    try:
        result = supabase.storage.from_(BUCKET_NAME).upload(
            filename,
            image_bytes,
            {"content-type": "image/jpeg", "upsert": "true"}
        )

        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(filename)
        return public_url

    except Exception as e:
        # If file exists, get the URL anyway
        if "Duplicate" in str(e) or "already exists" in str(e):
            return supabase.storage.from_(BUCKET_NAME).get_public_url(filename)
        print(f"    Upload error: {e}")
        return None


def main():
    print("=" * 60)
    print("Scientist Image Fetcher & Uploader")
    print("=" * 60)

    # Load scientists
    with open('scientist_db_rich.json', 'r', encoding='utf-8') as f:
        scientists = json.load(f)

    print(f"\nFound {len(scientists)} scientists")

    # Track progress
    success = 0
    failed = 0
    image_urls = {}  # Store URLs for updating JSON

    print("\nFetching and uploading images...\n")

    for i, scientist in enumerate(scientists):
        name = scientist.get("name", "")
        wiki_title = scientist.get("wiki_title", "")

        print(f"[{i+1}/{len(scientists)}] {name}", end=" ")

        # Get Wikipedia image URL
        wiki_image_url = get_wikipedia_image_url(name, wiki_title)

        if not wiki_image_url:
            print("- No image")
            failed += 1
            continue

        # Download image
        image_bytes = download_image(wiki_image_url)

        if not image_bytes:
            print("- Download failed")
            failed += 1
            continue

        # Create safe filename
        safe_name = name.lower().replace(" ", "_").replace(".", "").replace(",", "").replace("'", "")
        filename = f"{safe_name}.jpg"

        # Upload to Supabase
        public_url = upload_to_supabase(image_bytes, filename)

        if public_url:
            print("OK")
            image_urls[name] = public_url
            success += 1
        else:
            print("- Upload failed")
            failed += 1

        # Rate limiting
        time.sleep(0.3)

    # Update the JSON file with image URLs
    print("\nUpdating scientist database with image URLs...")
    for scientist in scientists:
        name = scientist.get("name", "")
        if name in image_urls:
            scientist["image_url"] = image_urls[name]

    with open('scientist_db_rich.json', 'w', encoding='utf-8') as f:
        json.dump(scientists, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("COMPLETE!")
    print(f"  Success: {success}")
    print(f"  Failed: {failed}")
    print(f"  Updated scientist_db_rich.json")
    print("=" * 60)


if __name__ == "__main__":
    main()
