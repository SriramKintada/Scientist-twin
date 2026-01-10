"""
Build Quality Scientist Database - 100% Image Coverage Required
Uses Wikipedia MCP + Firecrawl + Gemini to systematically add scientists
ONLY adds scientists with BOTH rich biography AND verified image
"""

import json
import os
import requests
import time
from dotenv import load_dotenv
from supabase import create_client
import google.generativeai as genai

load_dotenv()

# Setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BUCKET_NAME = "scientist-images"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

HEADERS = {'User-Agent': 'ScientistTwin/1.0 (contact@scirio.in)'}

# Load existing database
with open('scientist_db_rich.json', 'r', encoding='utf-8') as f:
    existing_scientists = json.load(f)
    existing_names = {s['name'].lower() for s in existing_scientists}

print(f"Starting with {len(existing_scientists)} existing scientists")
print(f"Scientists with images: {sum(1 for s in existing_scientists if s.get('image_url'))}")


def get_wikipedia_content_and_image(name: str):
    """Get Wikipedia article content and image URL using API"""
    api_url = "https://en.wikipedia.org/w/api.php"

    # Get page content
    params = {
        "action": "query",
        "titles": name,
        "prop": "extracts|pageimages",
        "exintro": False,
        "explaintext": True,
        "pithumbsize": 400,
        "format": "json"
    }

    try:
        response = requests.get(api_url, params=params, headers=HEADERS, timeout=10)
        data = response.json()

        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if page_id != "-1":
                content = page_data.get("extract", "")
                image_info = page_data.get("thumbnail", {})
                image_url = image_info.get("source", None)
                return content, image_url
    except Exception as e:
        print(f"    Wikipedia API error: {e}")

    return None, None


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
        # If already exists, get URL
        if "Duplicate" in str(e) or "already exists" in str(e):
            safe_name = scientist_name.lower().replace(" ", "_").replace(".", "").replace(",", "").replace("'", "")
            filename = f"{safe_name}.jpg"
            return supabase.storage.from_(BUCKET_NAME).get_public_url(filename)
        return None


def encode_scientist_traits(name: str, biography: str, field: str):
    """Use Gemini to encode scientist traits from biography"""

    prompt = f"""Analyze this Indian scientist's biography and encode their personality traits.

Scientist: {name}
Field: {field}

Biography:
{biography[:4000]}

Based on this biography, determine the scientist's traits across these 12 dimensions:

1. APPROACH: theoretical, experimental, applied, observational
2. COLLABORATION: solo, small_team, large_team, mentor
3. RISK: safety, calculated, bold, pioneering
4. MOTIVATION: curiosity, problem_solving, social_impact, recognition
5. ADVERSITY: persistent, adaptable, strategic, resilient
6. BREADTH: specialist, cross_disciplinary, polymath, integrator
7. AUTHORITY: challenger, builder, reformer, synthesizer
8. COMMUNICATION: technical, educator, public, advocate
9. TIME_HORIZON: immediate, medium, long_term, generational
10. RESOURCES: improviser, optimizer, collaborator_external, institution_builder
11. LEGACY: publications, students, institutions, cultural_change
12. FAILURE: iterative, pivot, fundamental_rethink, embrace

Return ONLY a JSON object with these 12 keys and their values, plus trait explanations.

Format:
{{
  "traits": {{"approach": "value", "collaboration": "value", ...}},
  "trait_explanations": {{
    "key_trait_1": "One sentence from biography",
    "key_trait_2": "One sentence from biography",
    "key_trait_3": "One sentence from biography"
  }},
  "era": "Pre-Independence Pioneer" or "Nation Builder" or "Modernization Era" or "Contemporary Leader",
  "summary": "2-3 sentence summary of their contribution"
}}"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Extract JSON
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        result = json.loads(text)
        return result

    except Exception as e:
        print(f"    Gemini encoding error: {e}")
        return None


# Priority scientists to add (from Wikipedia "List of Indian scientists")
# Focus on those with strong Wikipedia presence
PRIORITY_SCIENTISTS = [
    # Women scientists (HIGH PRIORITY)
    ("Sudha Murty", "Computer Science"),
    ("Kiran Mazumdar-Shaw", "Biotechnology"),
    ("Tessy Thomas", "Aerospace Engineering"),
    ("Ritu Karidhal", "Aerospace Engineering"),

    # Modern scientists with strong profiles
    ("Raghuram Rajan", "Economics"),
    ("Shrinivas Kulkarni", "Astronomy"),
    ("Vinod Dham", "Engineering"),
    ("Sabeer Bhatia", "Technology"),

    # Space scientists
    ("A. S. Kiran Kumar", "Aerospace"),
    ("K. Sivan", "Aerospace Engineering"),
    ("Mylswamy Annadurai", "Aerospace"),
]

print("\n" + "=" * 70)
print("BUILDING QUALITY DATABASE - 100% IMAGE COVERAGE REQUIRED")
print("=" * 70)

new_scientists = []
stats = {
    "processed": 0,
    "added": 0,
    "skipped_exists": 0,
    "skipped_no_image": 0,
    "skipped_no_bio": 0,
    "skipped_encoding_failed": 0
}

for name, field in PRIORITY_SCIENTISTS:
    stats["processed"] += 1
    print(f"\n[{stats['processed']}/{len(PRIORITY_SCIENTISTS)}] {name}")

    # Skip if exists
    if name.lower() in existing_names:
        print("  SKIP - Already in database")
        stats["skipped_exists"] += 1
        continue

    # Get biography and image
    print("  Fetching from Wikipedia...", end=" ")
    biography, image_url = get_wikipedia_content_and_image(name)

    if not biography or len(biography) < 300:
        print("SKIP - Insufficient biography")
        stats["skipped_no_bio"] += 1
        continue

    print(f"OK - Bio ({len(biography)} chars)")

    # Verify image
    print("  Checking image...", end=" ")
    if not image_url:
        print("SKIP - No image found")
        stats["skipped_no_image"] += 1
        continue

    print("OK - Found")

    # Upload image
    print("  Uploading to Supabase...", end=" ")
    supabase_url = download_and_upload_image(image_url, name)
    if not supabase_url:
        print("FAILED - Upload failed")
        stats["skipped_no_image"] += 1
        continue

    print("OK - Uploaded")

    # Encode traits
    print("  Encoding traits with Gemini...", end=" ")
    encoding = encode_scientist_traits(name, biography, field)
    if not encoding or "traits" not in encoding:
        print("FAILED - Encoding failed")
        stats["skipped_encoding_failed"] += 1
        continue

    print("OK - Encoded")

    # Create scientist entry
    scientist_entry = {
        "name": name,
        "field": field,
        "era": encoding.get("era", "Contemporary Leader"),
        "traits": encoding.get("traits", {}),
        "trait_explanations": encoding.get("trait_explanations", {}),
        "image_url": supabase_url,
        "summary": encoding.get("summary", biography[:200] + "..."),
        "biography_snippet": biography[:300].replace("\n", " ").strip() + "..."
    }

    new_scientists.append(scientist_entry)
    existing_names.add(name.lower())
    stats["added"] += 1

    print(f"  SUCCESS - ADDED - Total: {len(existing_scientists) + len(new_scientists)}")

    # Rate limiting
    time.sleep(2)


# Save updated database
if new_scientists:
    updated_db = existing_scientists + new_scientists

    with open('scientist_db_rich.json', 'w', encoding='utf-8') as f:
        json.dump(updated_db, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("DATABASE UPDATE COMPLETE")
    print("=" * 70)
    print(f"  Processed: {stats['processed']}")
    print(f"  Added: {stats['added']}")
    print(f"  Skipped (exists): {stats['skipped_exists']}")
    print(f"  Skipped (no image): {stats['skipped_no_image']}")
    print(f"  Skipped (no bio): {stats['skipped_no_bio']}")
    print(f"  Skipped (encoding failed): {stats['skipped_encoding_failed']}")
    print(f"\n  Total scientists: {len(updated_db)}")
    with_images = sum(1 for s in updated_db if s.get('image_url'))
    print(f"  With images: {with_images} ({with_images*100//len(updated_db)}%)")
    print("=" * 70)
else:
    print("\nNo new scientists added.")
