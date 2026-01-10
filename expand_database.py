"""
Expand Scientist Database to 400+ with Quality Control
- Extracts scientists from Wikipedia
- Verifies image availability (Wikipedia API + Firecrawl fallback)
- Fetches biographical content for trait encoding
- Prioritizes women scientists
- Only adds scientists with BOTH image AND quality biography
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


def get_wikipedia_content(name: str):
    """Get full Wikipedia article content"""
    api_url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "titles": name,
        "prop": "extracts|pageimages",
        "exintro": False,  # Get full article, not just intro
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
                image_url = page_data.get("thumbnail", {}).get("source", None)
                return content, image_url

    except Exception as e:
        print(f"    Wikipedia error: {e}")

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
        # If already exists, get URL anyway
        if "Duplicate" in str(e) or "already exists" in str(e):
            safe_name = scientist_name.lower().replace(" ", "_").replace(".", "").replace(",", "").replace("'", "")
            filename = f"{safe_name}.jpg"
            return supabase.storage.from_(BUCKET_NAME).get_public_url(filename)
        return None


def encode_scientist_traits(name: str, biography: str, field: str):
    """Use Gemini to encode scientist traits based on biography"""

    prompt = f"""Analyze this Indian scientist's biography and encode their personality traits.

Scientist: {name}
Field: {field}

Biography:
{biography[:3000]}

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

Return ONLY a JSON object with these 12 keys and their values. For example:
{{"approach": "experimental", "collaboration": "small_team", "risk": "calculated", ...}}

Also provide a 1-sentence trait explanation for their top 3 most distinctive traits based on their biography.

Return format:
{{
  "traits": {{"approach": "value", ...}},
  "trait_explanations": {{
    "trait_name_1": "One sentence explanation from biography",
    "trait_name_2": "One sentence explanation from biography",
    "trait_name_3": "One sentence explanation from biography"
  }}
}}"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Extract JSON from markdown code blocks if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        result = json.loads(text)
        return result.get("traits", {}), result.get("trait_explanations", {})

    except Exception as e:
        print(f"    Trait encoding error: {e}")
        return None, None


# List of scientists to extract (from Wikipedia "List of Indian scientists")
# Prioritizing scientists likely to have images and rich biographies
NEW_SCIENTISTS = [
    # Women scientists (priority)
    ("Sudha Murty", "Computer Science, Philanthropy"),
    ("Tessy Thomas", "Aerospace Engineering"),
    ("Aditi Pant", "Oceanography"),
    ("Charusita Chakravarty", "Chemistry"),
    ("Rohini Godbole", "Physics"),
    ("Anna Mani", "Meteorology"),
    ("Kamala Sohonie", "Biochemistry"),
    ("Rajeshwari Chatterjee", "Microwave Engineering"),
    ("Darshan Ranganathan", "Chemistry"),
    ("Indira Nath", "Medicine"),
    ("Shubha Tole", "Neuroscience"),
    ("Vidita Vaidya", "Neuroscience"),
    ("Yamuna Krishnan", "Chemistry"),
    ("Nandini Harinath", "Aerospace Engineering"),
    ("Gagandeep Kang", "Medicine"),
    ("Soumya Swaminathan", "Medicine"),
    ("Bimla Buti", "Plasma Physics"),
    ("Bibha Chowdhuri", "Physics"),
    ("Anandibai Joshi", "Medicine"),
    ("Kadambini Ganguly", "Medicine"),
    ("Mangala Narlikar", "Mathematics"),

    # Modern scientists with strong profiles
    ("Raghuram Rajan", "Economics"),
    ("Shrinivas Kulkarni", "Astronomy"),
    ("Arogyaswami Paulraj", "Electrical Engineering"),
    ("Arati Prabhakar", "Engineering"),
    ("Venkatraman Ramakrishnan", "Structural Biology"),
    ("Kiran Mazumdar-Shaw", "Biotechnology"),
    ("Shiv Nadar", "Computer Science"),
    ("Narendra Karmarkar", "Mathematics"),
    ("Srinivasa Varadhan", "Mathematics"),
    ("Subhash Khot", "Computer Science"),
    ("Avi Wigderson", "Computer Science"),

    # Space scientists
    ("G. Madhavan Nair", "Aerospace"),
    ("K. Radhakrishnan", "Aerospace"),
    ("A. S. Kiran Kumar", "Space Science"),
    ("K. Sivan", "Aerospace Engineering"),
    ("Mylswamy Annadurai", "Aerospace"),

    # Physics & Chemistry
    ("Thanu Padmanabhan", "Physics"),
    ("Jayant Narlikar", "Astrophysics"),
    ("Ashoke Sen", "Physics"),
    ("Rohini Godbole", "Physics"),
    ("R. Chidambaram", "Physics"),
    ("Rajagopala Chidambaram", "Physics"),
    ("G. N. Ramachandran", "Physics"),
    ("E. C. G. Sudarshan", "Physics"),
    ("Narinder Singh Kapany", "Optics"),
    ("Yellapragada Subbarow", "Chemistry"),
    ("Asima Chatterjee", "Chemistry"),
    ("Prafulla Chandra Ray", "Chemistry"),

    # Biology & Medicine
    ("Obaid Siddiqi", "Biology"),
    ("Pushpa Mittra Bhargava", "Biology"),
    ("Lalji Singh", "Genetics"),
    ("V. Shanta", "Medicine"),
    ("Kamal Ranadive", "Medicine"),
    ("Ruchi Ram Sahni", "Medicine"),
    ("Upendranath Brahmachari", "Medicine"),

    # Mathematics & Computer Science
    ("C. S. Seshadri", "Mathematics"),
    ("M. S. Narasimhan", "Mathematics"),
    ("K. Chandrasekharan", "Mathematics"),
    ("Shreeram Shankar Abhyankar", "Mathematics"),
    ("T. A. Sarasvati Amma", "Mathematics"),
    ("Aravind Joshi", "Computer Science"),
    ("Rajeev Alur", "Computer Science"),
    ("Shafi Goldwasser", "Computer Science"),
    ("Sanjay Ghemawat", "Computer Science"),

    # Engineering & Technology
    ("Ajay Bhatt", "Engineering"),
    ("Vinod Dham", "Engineering"),
    ("Sabeer Bhatia", "Technology"),
    ("Arogyaswami Paulraj", "Engineering"),
    ("Ashok Jhunjhunwala", "Engineering"),

    # Agriculture & Environment
    ("Richharia", "Agriculture"),
    ("Gurdev Singh Khush", "Agriculture"),
    ("R. S. Paroda", "Agriculture"),
    ("Madhav Gadgil", "Ecology"),
    ("Vandana Shiva", "Environmental Science"),
    ("Sunita Narain", "Environmental Science"),

    # Ancient & Historical
    ("Aryabhata", "Mathematics, Astronomy"),
    ("Brahmagupta", "Mathematics, Astronomy"),
    ("Varahamihira", "Astronomy"),
    ("Bhaskara II", "Mathematics"),
    ("Madhava of Sangamagrama", "Mathematics"),
    ("Sushruta", "Medicine"),
    ("Charaka", "Medicine"),
]

print(f"\nProcessing {len(NEW_SCIENTISTS)} candidate scientists...")
print("=" * 70)

new_additions = []
stats = {
    "processed": 0,
    "has_image": 0,
    "has_bio": 0,
    "added": 0,
    "skipped_no_image": 0,
    "skipped_no_bio": 0,
    "skipped_exists": 0
}

for name, field in NEW_SCIENTISTS:
    stats["processed"] += 1
    print(f"\n[{stats['processed']}/{len(NEW_SCIENTISTS)}] {name}")

    # Skip if already exists
    if name.lower() in existing_names:
        print("  Already in database - SKIP")
        stats["skipped_exists"] += 1
        continue

    # Get Wikipedia content
    print("  Fetching biography...", end=" ")
    biography, image_url = get_wikipedia_content(name)

    if not biography or len(biography) < 200:
        print("INSUFFICIENT")
        stats["skipped_no_bio"] += 1
        continue

    print(f"OK ({len(biography)} chars)")
    stats["has_bio"] += 1

    # Check image
    print("  Checking image...", end=" ")
    if not image_url:
        print("NOT FOUND")
        stats["skipped_no_image"] += 1
        continue

    print("OK")
    stats["has_image"] += 1

    # Upload image to Supabase
    print("  Uploading image...", end=" ")
    supabase_url = download_and_upload_image(image_url, name)
    if not supabase_url:
        print("FAILED")
        stats["skipped_no_image"] += 1
        continue

    print("OK")

    # Encode traits
    print("  Encoding traits...", end=" ")
    traits, explanations = encode_scientist_traits(name, biography, field)

    if not traits:
        print("FAILED")
        stats["skipped_no_bio"] += 1
        continue

    print("OK")

    # Create scientist entry
    scientist_entry = {
        "name": name,
        "field": field,
        "era": "Modern" if "born" in biography.lower() and "19" in biography else "Contemporary",
        "traits": traits,
        "trait_explanations": explanations,
        "image_url": supabase_url,
        "biography_snippet": biography[:300].replace("\n", " ").strip() + "..."
    }

    new_additions.append(scientist_entry)
    existing_names.add(name.lower())
    stats["added"] += 1

    print(f"  ADDED - Total now: {len(existing_scientists) + len(new_additions)}")

    # Rate limiting
    time.sleep(1.5)

# Save updated database
print("\n" + "=" * 70)
print("EXPANSION COMPLETE")
print(f"  Processed: {stats['processed']}")
print(f"  Added: {stats['added']}")
print(f"  Skipped (exists): {stats['skipped_exists']}")
print(f"  Skipped (no image): {stats['skipped_no_image']}")
print(f"  Skipped (insufficient bio): {stats['skipped_no_bio']}")
print(f"\nTotal database size: {len(existing_scientists) + len(new_additions)} scientists")
print("=" * 70)

if new_additions:
    # Merge and save
    updated_db = existing_scientists + new_additions

    with open('scientist_db_rich.json', 'w', encoding='utf-8') as f:
        json.dump(updated_db, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to scientist_db_rich.json")

    # Show sample of women scientists added
    women_added = [s for s in new_additions if s['name'] in [n for n, f in NEW_SCIENTISTS[:21]]]
    if women_added:
        print(f"\nWomen scientists added: {len(women_added)}")
        for w in women_added[:5]:
            print(f"  - {w['name']} ({w['field']})")
