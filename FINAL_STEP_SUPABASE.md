# Final Step: Upload Images to Supabase

## ✅ What's Been Completed

1. **✅ Found images for all 42 scientists** using Firecrawl
2. **✅ Updated local database** - all 195 scientists now have `image_url`
3. **✅ Pushed to GitHub** - commit ac99bbf
4. **✅ Created automated upload script** - `complete_image_upload.py`

## ⏳ Final Step Required

**Upload the 195 image URLs to Supabase database**

This requires ONE command but needs your Supabase database password.

---

## Option 1: Automated Script (Recommended)

Run this single command:

```bash
cd C:\Users\kinta\OneDrive\Desktop\Scn\scientist_twin
python complete_image_upload.py
```

**What it does:**
1. Prompts for your Supabase database password
2. Connects directly to PostgreSQL
3. Adds the `image_url` column
4. Uploads all 195 image URLs
5. Verifies completion

**Get your database password:**
1. Go to: https://supabase.com/dashboard/project/nlgcvxygeicujcqwomut/settings/database
2. Log in to Supabase
3. Look for "Database password" section
4. Copy the password (or reset it if you don't have it)

---

## Option 2: Manual SQL (If script fails)

### Step 1: Add Column
Go to: https://supabase.com/dashboard/project/nlgcvxygeicujcqwomut/sql/new

Run this SQL:
```sql
ALTER TABLE scientists ADD COLUMN image_url TEXT;
```

### Step 2: Upload Images
Then run:
```bash
python add_images_to_supabase.py
```

---

## Verification

After running the script, verify:

```python
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Check random scientists
result = supabase.table('scientists').select('name, image_url').limit(5).execute()
for scientist in result.data:
    print(f"{scientist['name']}: {scientist['image_url'][:50]}...")
```

---

## Summary

**Local Database:** ✅ 195/195 scientists with images
**GitHub:** ✅ Pushed successfully
**Supabase:** ⏳ Waiting for password to complete upload

**Once complete, all 195 scientists will display with images in the quiz!**
