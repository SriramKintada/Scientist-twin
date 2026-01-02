"""
Upload priority scientist images (full resolution from Wikipedia)
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

# Full resolution image URLs from Wikipedia articles
PRIORITY_IMAGES = {
    "Kamala Sohonie": "https://upload.wikimedia.org/wikipedia/en/9/99/Kamala_Sohonie.jpg",
    "Kamal Ranadive": "https://upload.wikimedia.org/wikipedia/en/e/e6/Kamal_Ranadive.jpg",
    "Rajeshwari Chatterjee": "https://upload.wikimedia.org/wikipedia/en/4/42/Rajeshwari_Chatterjee_image.jpg",
    "Bimla Buti": "https://upload.wikimedia.org/wikipedia/en/9/92/Bimla_Buti.jpg",
    "Gagandeep Kang": "https://upload.wikimedia.org/wikipedia/commons/a/a6/Gagandeep_Kang.jpg",
    "K. S. Krishnan": "https://upload.wikimedia.org/wikipedia/en/9/90/Kariamanickam_Srinivasa_Krishnan.jpg",
    "Venkatraman Ramakrishnan": "https://upload.wikimedia.org/wikipedia/commons/1/12/Venki_Ramakrishnan_by_Thomas_Shahan_3.jpg",
    "Shanti Swaroop Bhatnagar": "https://upload.wikimedia.org/wikipedia/en/2/24/Shanti_Swarup_Bhatnagar_-_Kolkata_2011-02-09_0782.JPG",
    "Darshan Ranganathan": "https://upload.wikimedia.org/wikipedia/en/e/e0/Darshan_Ranganathan.jpg",
    "Salim Ali": "https://upload.wikimedia.org/wikipedia/commons/5/50/Salim_Ali2.jpg",
    "Obaid Siddiqi": "https://upload.wikimedia.org/wikipedia/en/0/00/Obaid_Siddiqi_%28cropped%29.jpg",
    "K. VijayRaghavan": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Dr._K_Vijayraghavan.jpg",
    "M. G. K. Menon": "https://upload.wikimedia.org/wikipedia/en/3/32/MGK_Menon.jpg",
    "Nitya Anand": "https://upload.wikimedia.org/wikipedia/en/5/5f/Nitya_Anand.jpg",
    "K. Kasturirangan": "https://upload.wikimedia.org/wikipedia/commons/3/3a/K._Kasturirangan.jpg",
    "Sivathanu Pillai": "https://upload.wikimedia.org/wikipedia/commons/3/3d/A._Sivathanu_Pillai.jpg",
    "Umesh Vazirani": "https://upload.wikimedia.org/wikipedia/commons/8/88/Umesh_Vazirani.jpg",
    "D. N. Wadia": "https://upload.wikimedia.org/wikipedia/en/2/27/Darashaw_Nosherwan_Wadia.jpg",
    "Aditi Pant": "https://upload.wikimedia.org/wikipedia/en/8/8e/Aditi_Pant.jpg",
    "Anandibai Joshi": "https://upload.wikimedia.org/wikipedia/commons/5/51/Anandibai_Joshee_%28cropped%29.jpg",
    "U. R. Rao": "https://upload.wikimedia.org/wikipedia/commons/2/28/U._R._Rao.jpg",
    "K. Radhakrishnan": "https://upload.wikimedia.org/wikipedia/commons/2/2b/Dr._K._Radhakrishnan_-_cropped.jpg",
    "Homi N. Sethna": "https://upload.wikimedia.org/wikipedia/en/3/3f/Homi_N._Sethna.jpg",
    "G. N. Ramachandran": "https://upload.wikimedia.org/wikipedia/en/c/c7/GNRamachandran.jpg",
    "Raja Ramanna": "https://upload.wikimedia.org/wikipedia/commons/d/d4/Dr._Raja_Ramanna.jpg",
    "P. K. Iyengar": "https://upload.wikimedia.org/wikipedia/en/b/bc/Dr_P_K_Iyengar.jpg",
    "Narinder Singh Kapany": "https://upload.wikimedia.org/wikipedia/en/f/fd/Narinder_Singh_Kapany_in_his_laboratory.jpg",
    "D. S. Kothari": "https://upload.wikimedia.org/wikipedia/en/5/58/Daulat_Singh_Kothari.jpg"
}


def download_and_upload_image(image_url: str, scientist_name: str) -> str:
    """Download image and upload to Supabase"""
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

print("=" * 70)
print("PRIORITY IMAGE UPLOADER (Full Resolution)")
print("=" * 70)

updated = 0
failed = []

for scientist in scientists:
    name = scientist.get('name')

    # Skip if already has image
    if scientist.get('image_url'):
        continue

    # Check if we have a priority image URL
    if name in PRIORITY_IMAGES:
        print(f"\n{name}")
        print(f"  Uploading...", end=" ")

        supabase_url = download_and_upload_image(PRIORITY_IMAGES[name], name)

        if supabase_url:
            scientist['image_url'] = supabase_url
            updated += 1
            print("OK")
        else:
            failed.append(name)
            print("FAILED")

# Save updated database
with open('scientist_db_rich.json', 'w', encoding='utf-8') as f:
    json.dump(scientists, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 70)
print(f"Updated: {updated} scientists")
print(f"Failed: {len(failed)}")
if failed:
    print(f"Failed scientists: {', '.join(failed)}")
print("=" * 70)

# Count total with images
with_images = sum(1 for s in scientists if s.get('image_url'))
total = len(scientists)
print(f"\nTotal scientists: {total}")
print(f"With images: {with_images} ({with_images*100//total}%)")
print(f"Missing images: {total - with_images}")
