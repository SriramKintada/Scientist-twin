"""
Fetch missing images for existing scientists using Firecrawl
"""

import json
import os
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = "scientist-images"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
HEADERS = {'User-Agent': 'ScientistTwin/1.0 (contact@scirio.in)'}

# Load scientists
with open('scientist_db_rich.json', 'r', encoding='utf-8') as f:
    scientists = json.load(f)

# Find scientists without images
missing_images = [s for s in scientists if not s.get('image_url')]

print(f"Found {len(missing_images)} scientists without images")
print("\nList of scientists missing images:")
for i, s in enumerate(missing_images[:50], 1):
    print(f"{i}. {s['name']} ({s['field']})")

# Save list to file for Firecrawl processing
with open('missing_images_list.json', 'w', encoding='utf-8') as f:
    json.dump([{
        "name": s['name'],
        "field": s['field'],
        "wiki_title": s.get('wiki_title', s['name'])
    } for s in missing_images], f, indent=2)

print(f"\nSaved list to missing_images_list.json")
print(f"\nTotal scientists needing images: {len(missing_images)}")
