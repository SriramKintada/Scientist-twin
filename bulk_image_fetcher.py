"""
Bulk fetch missing scientist images using Wikipedia API + manual URLs
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

# Known image URLs from Firecrawl and Wikipedia
KNOWN_IMAGES = {
    "R. C. Bose": "https://upload.wikimedia.org/wikipedia/en/d/d3/Raj_Chandra_Bose.jpg",
    "Anna Mani": "https://upload.wikimedia.org/wikipedia/en/6/67/Anna_Mani.jpg",
    "Asima Chatterjee": "https://upload.wikimedia.org/wikipedia/en/7/7d/Asima_Chatterjee_1.jpg",
    "Kamala Sohonie": "https://upload.wikimedia.org/wikipedia/en/9/99/Kamala_Sohonie.jpg",
    "Bhama Srinivasan": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Bhama_Srinivasan.jpg/400px-Bhama_Srinivasan.jpg",
    "K. S. Krishnan": "https://upload.wikimedia.org/wikipedia/en/thumb/9/90/Kariamanickam_Srinivasa_Krishnan.jpg/400px-Kariamanickam_Srinivasa_Krishnan.jpg",
    "G. N. Ramachandran": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c7/GNRamachandran.jpg/400px-GNRamachandran.jpg",
    "Raja Ramanna": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Dr._Raja_Ramanna.jpg/400px-Dr._Raja_Ramanna.jpg",
    "P. K. Iyengar": "https://upload.wikimedia.org/wikipedia/en/thumb/b/bc/Dr_P_K_Iyengar.jpg/400px-Dr_P_K_Iyengar.jpg",
    "Bimla Buti": "https://upload.wikimedia.org/wikipedia/en/thumb/9/92/Bimla_Buti.jpg/400px-Bimla_Buti.jpg",
    "Narinder Singh Kapany": "https://upload.wikimedia.org/wikipedia/en/thumb/f/fd/Narinder_Singh_Kapany_in_his_laboratory.jpg/400px-Narinder_Singh_Kapany_in_his_laboratory.jpg",
    "D. S. Kothari": "https://upload.wikimedia.org/wikipedia/en/thumb/5/58/Daulat_Singh_Kothari.jpg/400px-Daulat_Singh_Kothari.jpg",
    "Venkatraman Ramakrishnan": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Venki_Ramakrishnan_by_Thomas_Shahan_3.jpg/400px-Venki_Ramakrishnan_by_Thomas_Shahan_3.jpg",
    "Shanti Swaroop Bhatnagar": "https://upload.wikimedia.org/wikipedia/en/thumb/2/24/Shanti_Swarup_Bhatnagar_-_Kolkata_2011-02-09_0782.JPG/400px-Shanti_Swarup_Bhatnagar_-_Kolkata_2011-02-09_0782.JPG",
    "Darshan Ranganathan": "https://upload.wikimedia.org/wikipedia/en/thumb/e/e0/Darshan_Ranganathan.jpg/400px-Darshan_Ranganathan.jpg",
    "Salim Ali": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Salim_Ali2.jpg/400px-Salim_Ali2.jpg",
    "Obaid Siddiqi": "https://upload.wikimedia.org/wikipedia/en/thumb/0/00/Obaid_Siddiqi_%28cropped%29.jpg/400px-Obaid_Siddiqi_%28cropped%29.jpg",
    "Kamal Ranadive": "https://upload.wikimedia.org/wikipedia/en/thumb/9/91/Kamal_Ranadive.jpg/400px-Kamal_Ranadive.jpg",
    "Gagandeep Kang": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Gagandeep_Kang.jpg/400px-Gagandeep_Kang.jpg",
    "K. VijayRaghavan": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Dr._K_Vijayraghavan.jpg/400px-Dr._K_Vijayraghavan.jpg",
    "M. G. K. Menon": "https://upload.wikimedia.org/wikipedia/en/thumb/3/32/MGK_Menon.jpg/400px-MGK_Menon.jpg",
    "Nitya Anand": "https://upload.wikimedia.org/wikipedia/en/thumb/5/5f/Nitya_Anand.jpg/400px-Nitya_Anand.jpg",
    "K. Kasturirangan": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/K._Kasturirangan.jpg/400px-K._Kasturirangan.jpg",
    "Sivathanu Pillai": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/A._Sivathanu_Pillai.jpg/400px-A._Sivathanu_Pillai.jpg",
    "Umesh Vazirani": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Umesh_Vazirani.jpg/400px-Umesh_Vazirani.jpg",
    "Rajeshwari Chatterjee": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a3/Rajeshwari_Chatterjee.jpg/400px-Rajeshwari_Chatterjee.jpg",
    "D. N. Wadia": "https://upload.wikimedia.org/wikipedia/en/thumb/2/27/Darashaw_Nosherwan_Wadia.jpg/400px-Darashaw_Nosherwan_Wadia.jpg",
    "M. S. Krishnan": "https://upload.wikimedia.org/wikipedia/en/thumb/5/52/Maniyani_Parameswaran_Subbiah.jpg/400px-Maniyani_Parameswaran_Subbiah.jpg",
    "Aditi Pant": "https://upload.wikimedia.org/wikipedia/en/thumb/8/8e/Aditi_Pant.jpg/400px-Aditi_Pant.jpg",
    "S. K. Sinha": "https://upload.wikimedia.org/wikipedia/en/thumb/3/3d/Dr_SK_Sinha.jpg/400px-Dr_SK_Sinha.jpg",
    "K. Venkataraman": "https://upload.wikimedia.org/wikipedia/en/thumb/4/4e/Kadanahalli_Venkataraman.jpg/400px-Kadanahalli_Venkataraman.jpg",
    "R. Parimala": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Raman_Parimala.jpg/400px-Raman_Parimala.jpg",
    "Venki Ramakrishnan": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Venki_Ramakrishnan_by_Thomas_Shahan_3.jpg/400px-Venki_Ramakrishnan_by_Thomas_Shahan_3.jpg",
    "Anandibai Joshi": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Anandibai_Joshee_%28cropped%29.jpg/400px-Anandibai_Joshee_%28cropped%29.jpg",
    "Brahmagupta": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Brahmagupta_-_Nuremberg_Chronicle.jpg/400px-Brahmagupta_-_Nuremberg_Chronicle.jpg",
    "Varahamihira": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Varaha_Mihira_-_Statue_at_the_Inter-University_Centre_for_Astronomy_and_Astrophysics_%28IUCAA%29_Pune_-_20131227.jpg/400px-Varaha_Mihira_-_Statue_at_the_Inter-University_Centre_for_Astronomy_and_Astrophysics_%28IUCAA%29_Pune_-_20131227.jpg",
    "Madhava": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/Madhava_of_Sangamagrama.jpg/400px-Madhava_of_Sangamagrama.jpg",
    "U. R. Rao": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/U._R._Rao.jpg/400px-U._R._Rao.jpg",
    "K. Radhakrishnan": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Dr._K._Radhakrishnan_-_cropped.jpg/400px-Dr._K._Radhakrishnan_-_cropped.jpg",
    "Homi N. Sethna": "https://upload.wikimedia.org/wikipedia/en/thumb/3/3f/Homi_N._Sethna.jpg/400px-Homi_N._Sethna.jpg"
}


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

print("=" * 70)
print("BULK IMAGE UPLOADER")
print("=" * 70)

updated = 0
failed = []

for scientist in scientists:
    name = scientist.get('name')

    # Skip if already has image
    if scientist.get('image_url'):
        continue

    # Check if we have a known image URL
    if name in KNOWN_IMAGES:
        print(f"\n{name}")
        print(f"  Uploading from known URL...", end=" ")

        supabase_url = download_and_upload_image(KNOWN_IMAGES[name], name)

        if supabase_url:
            scientist['image_url'] = supabase_url
            updated += 1
            print("OK")
        else:
            failed.append(name)
            print("FAILED")

        time.sleep(0.5)

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
