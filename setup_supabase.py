"""
Setup script for Supabase integration
Run this after creating your Supabase project and running the schema SQL
"""

import json
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    print("=" * 60)
    print("Scientist Twin - Supabase Setup")
    print("=" * 60)

    # Check environment variables
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_KEY", "")

    if not supabase_url or not supabase_key:
        print("\n[ERROR] Supabase credentials not found!")
        print("\nPlease add to your .env file:")
        print("  SUPABASE_URL=https://your-project.supabase.co")
        print("  SUPABASE_KEY=your_supabase_anon_key")
        print("\nYou can find these in your Supabase project settings.")
        return

    print(f"\n[OK] Supabase URL: {supabase_url[:40]}...")
    print(f"[OK] Supabase Key: {supabase_key[:20]}...")

    # Test connection
    print("\n[Step 1] Testing connection...")
    try:
        from supabase import create_client
        client = create_client(supabase_url, supabase_key)
        print("[OK] Connected to Supabase!")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return

    # Check if schema exists
    print("\n[Step 2] Checking database schema...")
    try:
        result = client.table("scientists").select("id").limit(1).execute()
        print("[OK] 'scientists' table exists")
    except Exception as e:
        print(f"[WARNING] Schema might not be set up: {e}")
        print("\nPlease run the SQL schema first:")
        print("  1. Go to your Supabase Dashboard")
        print("  2. Click on 'SQL Editor'")
        print("  3. Paste contents of 'supabase_schema.sql'")
        print("  4. Click 'Run'")
        print("\nThen run this script again.")
        return

    # Upload scientists
    print("\n[Step 3] Uploading scientists to Supabase...")
    try:
        with open('scientist_db_rich.json', 'r', encoding='utf-8') as f:
            scientists = json.load(f)

        print(f"Found {len(scientists)} scientists to upload")

        uploaded = 0
        errors = 0
        for i, scientist in enumerate(scientists):
            try:
                # Prepare data for Supabase
                data = {
                    "name": scientist.get("name", ""),
                    "field": scientist.get("field", ""),
                    "subfield": scientist.get("subfield", ""),
                    "era": scientist.get("era", ""),
                    "archetype": scientist.get("archetype", ""),
                    "summary": scientist.get("summary", ""),
                    "achievements": scientist.get("achievements", ""),
                    "working_style": scientist.get("working_style", ""),
                    "traits": scientist.get("traits", {}),
                    "moments": scientist.get("moments", []),
                    "wiki_title": scientist.get("wiki_title", "")
                }

                # Upsert (insert or update)
                client.table("scientists").upsert(data, on_conflict="name").execute()
                uploaded += 1

                if (i + 1) % 20 == 0:
                    print(f"  Uploaded {i + 1}/{len(scientists)}...")

            except Exception as e:
                errors += 1
                print(f"  [ERROR] {scientist.get('name', 'Unknown')}: {e}")

        print(f"\n[OK] Uploaded {uploaded} scientists ({errors} errors)")

    except FileNotFoundError:
        print("[ERROR] scientist_db_rich.json not found!")
        return

    # Generate embeddings (if sentence-transformers available)
    print("\n[Step 4] Generating embeddings...")
    try:
        from generate_embeddings import generate_all_embeddings, upload_embeddings_to_supabase

        embeddings = generate_all_embeddings()
        upload_embeddings_to_supabase(embeddings)
        print("[OK] Embeddings generated and uploaded!")

    except ImportError:
        print("[SKIP] sentence-transformers not installed")
        print("  Run: pip install sentence-transformers")
        print("  Then run: python generate_embeddings.py")

    except Exception as e:
        print(f"[WARNING] Embedding generation failed: {e}")
        print("  You can run this later: python generate_embeddings.py")

    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("\nYour Scientist Twin app now has:")
    print("  - Real analytics (plays, likes, shares tracked)")
    print("  - Persistent user data")
    print("  - Vector search for semantic matching")
    print("\nStart the app: python web_app_v3.py")


if __name__ == "__main__":
    main()
