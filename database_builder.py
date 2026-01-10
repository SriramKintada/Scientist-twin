"""
Database Builder - Fetches Wikipedia data and builds rich scientist profiles
Uses wikipediaapi package for reliable data fetching
"""

import json
import wikipediaapi
import time
import re
from typing import Optional, Dict, List

# Import processing functions from build script
from build_1000_scientists import (
    UNIQUE_SCIENTISTS,
    infer_traits_from_text,
    extract_achievements,
    extract_key_moments,
    extract_summary,
    determine_archetype,
    determine_era,
    extract_working_style
)

# Initialize Wikipedia API with user agent
wiki = wikipediaapi.Wikipedia(
    user_agent='ScientistTwin/1.0 (https://github.com/scientist-twin; contact@example.com)',
    language='en'
)

def fetch_wikipedia_full(title: str) -> Optional[str]:
    """Fetch full Wikipedia content using wikipediaapi"""
    try:
        page = wiki.page(title)
        if page.exists():
            return page.text
        return None
    except Exception as e:
        print(f"  Error fetching {title}: {e}")
        return None

def process_scientist(scientist_info: dict) -> Optional[dict]:
    """Process a single scientist and create rich profile"""
    name = scientist_info["name"]
    wiki_title = scientist_info["wiki"]
    field = scientist_info["field"]
    subfield = scientist_info["subfield"]

    # Fetch Wikipedia content
    content = fetch_wikipedia_full(wiki_title)

    if not content or len(content) < 200:
        print(f"  Insufficient content for {name}")
        return None

    # Process the content
    traits = infer_traits_from_text(content)
    achievements = extract_achievements(content)
    moments = extract_key_moments(content)
    summary = extract_summary(content)
    archetype = determine_archetype(traits, field)
    era = determine_era(content)
    working_style = extract_working_style(content, name)

    # Quality check
    if len(summary) < 100:
        print(f"  Summary too short for {name}")
        return None

    return {
        "name": name,
        "field": field,
        "subfield": subfield,
        "wiki_title": wiki_title,  # Store wiki title for Wikipedia link
        "traits": traits,
        "archetype": archetype,
        "era": era,
        "achievements": achievements if achievements else f"Distinguished contributions to {subfield}",
        "summary": summary,
        "moments": moments,
        "working_style": working_style,
        "content_length": len(content)
    }

def build_database(target_count: int = 400, output_file: str = "scientist_db_rich.json"):
    """Build the scientist database"""
    print(f"\n{'='*60}")
    print(f"Building Scientist Database")
    print(f"Target: {target_count} scientists with quality profiles")
    print(f"{'='*60}\n")

    scientists = []
    processed = 0
    failed = 0

    for i, scientist_info in enumerate(UNIQUE_SCIENTISTS):
        if len(scientists) >= target_count:
            break

        print(f"[{i+1}/{len(UNIQUE_SCIENTISTS)}] Processing {scientist_info['name']}...", end=" ")

        profile = process_scientist(scientist_info)

        if profile:
            scientists.append(profile)
            print(f"OK ({profile['content_length']} chars)")
        else:
            failed += 1
            print("SKIPPED")

        processed += 1

        # Rate limiting
        if processed % 10 == 0:
            time.sleep(1)

    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(scientists, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"Database Build Complete!")
    print(f"{'='*60}")
    print(f"Total processed: {processed}")
    print(f"Successful: {len(scientists)}")
    print(f"Failed/Skipped: {failed}")
    print(f"Output file: {output_file}")

    # Stats by field
    field_counts = {}
    for s in scientists:
        field = s['field']
        field_counts[field] = field_counts.get(field, 0) + 1

    print(f"\nBy Field:")
    for field, count in sorted(field_counts.items(), key=lambda x: -x[1]):
        print(f"  {field}: {count}")

    return scientists

if __name__ == "__main__":
    # Build database targeting 400 scientists
    scientists = build_database(target_count=400)

    print(f"\n\nSample profiles:")
    for s in scientists[:3]:
        print(f"\n--- {s['name']} ---")
        print(f"Field: {s['field']} / {s['subfield']}")
        print(f"Archetype: {s['archetype']}")
        print(f"Era: {s['era']}")
        print(f"Summary: {s['summary'][:200]}...")
