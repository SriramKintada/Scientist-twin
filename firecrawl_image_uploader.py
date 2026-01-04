"""
Use Firecrawl MCP to fetch scientist images from Wikipedia
Extracts og:image metadata from Wikipedia pages and uploads to Supabase
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


def get_wikipedia_image_url(scientist_name: str) -> str:
    """
    Get scientist image URL from Wikipedia using Firecrawl.
    This function simulates what Firecrawl would return - you need to call Firecrawl MCP separately.
    """
    # Wikipedia URL format
    wiki_name = scientist_name.replace(" ", "_")
    return f"https://en.wikipedia.org/wiki/{wiki_name}"


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
print("FIRECRAWL IMAGE UPLOADER")
print("=" * 70)
print(f"Scientists missing images: {len(missing_images)}")
print("\nGENERATE WIKIPEDIA URLS TO FETCH WITH FIRECRAWL:")
print("=" * 70)

# Output Wikipedia URLs for Firecrawl batch processing
for scientist in missing_images[:50]:  # Process first 50
    wiki_url = get_wikipedia_image_url(scientist['name'])
    print(wiki_url)

print("=" * 70)
print("\nUSE FIRECRAWL MCP TO SCRAPE THESE URLS AND EXTRACT og:image METADATA")
print("THEN RUN IMAGE UPLOAD MANUALLY WITH EXTRACTED URLS")
