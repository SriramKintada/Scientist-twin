"""
COMPLETE AUTOMATED IMAGE UPLOAD TO SUPABASE
Run this script to finish uploading all 195 scientist images to Supabase

This script will:
1. Connect to Supabase PostgreSQL database directly
2. Add the image_url column
3. Upload all image URLs

Just run: python complete_image_upload.py [database_password]
Or it will prompt you for the password.

Get your database password from:
https://supabase.com/dashboard/project/nlgcvxygeicujcqwomut/settings/database
Click "Reset database password" if needed.
"""

import json
import sys
import psycopg2
from psycopg2 import sql

def main():
    print("=" * 70)
    print("COMPLETE AUTOMATED IMAGE UPLOAD TO SUPABASE")
    print("=" * 70)

    # Get database password
    if len(sys.argv) > 1:
        db_password = sys.argv[1]
    else:
        print("\nDatabase password required.")
        print("Get it from: https://supabase.com/dashboard/project/nlgcvxygeicujcqwomut/settings/database")
        db_password = input("\nEnter database password: ").strip()

    if not db_password:
        print("ERROR: Password cannot be empty")
        return

    # Supabase connection details
    project_ref = "nlgcvxygeicujcqwomut"
    region = "us-west-1"  # Change if your project is in a different region

    # Connection string
    conn_string = f"postgresql://postgres.{project_ref}:{db_password}@aws-0-{region}.pooler.supabase.com:6543/postgres"

    try:
        print("\n[1/3] Connecting to Supabase PostgreSQL database...")
        conn = psycopg2.connect(conn_string)
        conn.autocommit = True
        cur = conn.cursor()
        print("SUCCESS - Connected to database!")

        # Step 1: Add column
        print("\n[2/3] Adding image_url column to scientists table...")
        try:
            cur.execute("ALTER TABLE scientists ADD COLUMN IF NOT EXISTS image_url TEXT;")
            print("SUCCESS - Column added!")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("INFO - Column already exists, skipping...")
            else:
                raise e

        # Step 2: Load and upload images
        print("\n[3/3] Uploading image URLs...")

        with open('scientist_db_rich.json', 'r', encoding='utf-8') as f:
            scientists = json.load(f)

        print(f"Found {len(scientists)} scientists in local database")

        success_count = 0
        error_count = 0

        for i, scientist in enumerate(scientists, 1):
            name = scientist['name']
            image_url = scientist.get('image_url', '')

            try:
                cur.execute(
                    "UPDATE scientists SET image_url = %s WHERE name = %s;",
                    (image_url, name)
                )
                success_count += 1

                if i % 20 == 0:
                    print(f"  Progress: {i}/{len(scientists)} scientists updated...")

            except Exception as e:
                error_count += 1
                print(f"  ERROR updating {name}: {e}")

        # Close connection
        cur.close()
        conn.close()

        # Summary
        print("\n" + "=" * 70)
        print("UPLOAD COMPLETE!")
        print("=" * 70)
        print(f"Successfully updated: {success_count}/{len(scientists)} scientists")
        print(f"Errors: {error_count}")

        if error_count == 0:
            print("\nSUCCESS! All 195 scientist images are now in Supabase!")
            print("Your app is ready to display images for all scientists.")
        else:
            print(f"\nWARNING: {error_count} scientists failed. Check errors above.")

    except psycopg2.OperationalError as e:
        if "password authentication failed" in str(e):
            print("\nERROR: Invalid database password")
            print("Get the correct password from Supabase dashboard")
        else:
            print(f"\nERROR: Could not connect to database: {e}")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
