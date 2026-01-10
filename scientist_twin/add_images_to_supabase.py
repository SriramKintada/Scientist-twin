"""
Complete script to add image_url column and upload all images to Supabase
Run this script once to complete the image upload process
"""

import json
import os
from supabase import create_client, Client
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()

    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')

    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return

    # Connect to Supabase
    supabase: Client = create_client(url, key)

    print("=" * 60)
    print("SUPABASE IMAGE UPLOAD SCRIPT")
    print("=" * 60)

    # Step 1: Check if column exists
    print("\n[1/3] Checking if image_url column exists...")
    try:
        result = supabase.table('scientists').select('name, image_url').limit(1).execute()
        print("OK - Column already exists!")
        column_exists = True
    except Exception as e:
        if 'does not exist' in str(e):
            print("Column does not exist - needs to be added")
            column_exists = False
        else:
            print(f"Error: {e}")
            return

    # Step 2: Add column if needed
    if not column_exists:
        print("\n[2/3] Adding image_url column...")
        print("\nIMPORTANT: Please run this SQL command in Supabase SQL Editor:")
        print("-" * 60)
        print("ALTER TABLE scientists ADD COLUMN image_url TEXT;")
        print("-" * 60)
        print("\nSteps:")
        print("1. Go to: https://supabase.com/dashboard/project/nlgcvxygeicujcqwomut/sql/new")
        print("2. Paste the SQL command above")
        print("3. Click 'Run'")
        print("4. Press Enter here to continue...")

        input()

        # Verify column was added
        try:
            result = supabase.table('scientists').select('name, image_url').limit(1).execute()
            print("OK - Column verified!")
        except Exception as e:
            print(f"ERROR - Column still not found. Please run the SQL command first.")
            return

    # Step 3: Load and upload images
    print("\n[3/3] Uploading image URLs to Supabase...")

    # Load local database
    with open('scientist_db_rich.json', 'r', encoding='utf-8') as f:
        scientists = json.load(f)

    print(f"Found {len(scientists)} scientists in local database")

    # Update all scientists with image URLs
    success_count = 0
    error_count = 0

    for i, scientist in enumerate(scientists, 1):
        name = scientist['name']
        image_url = scientist.get('image_url', '')

        try:
            result = supabase.table('scientists').update({
                'image_url': image_url
            }).eq('name', name).execute()

            if result.data:
                success_count += 1
                if i % 20 == 0:
                    print(f"  Progress: {i}/{len(scientists)} scientists updated...")
            else:
                error_count += 1
                print(f"  Warning: No data returned for {name}")

        except Exception as e:
            error_count += 1
            print(f"  Error updating {name}: {e}")

    print("\n" + "=" * 60)
    print("UPLOAD COMPLETE!")
    print("=" * 60)
    print(f"Successfully updated: {success_count}/{len(scientists)} scientists")
    print(f"Errors: {error_count}")

    if error_count == 0:
        print("\nSUCCESS! All images successfully uploaded to Supabase!")
    else:
        print(f"\nWARNING: {error_count} scientists failed to update. Check errors above.")

if __name__ == "__main__":
    main()
