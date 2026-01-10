"""
Fetch Wikipedia data for scientists and build rich database
This script will be used to collect data, then we'll process it
"""

import json
import os

# Import from our build script
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

def process_wikipedia_content(name: str, field: str, subfield: str, wiki_content: str) -> dict:
    """Process Wikipedia content into a rich scientist profile"""

    if not wiki_content or len(wiki_content) < 100:
        return None

    # Extract all the rich data
    traits = infer_traits_from_text(wiki_content)
    achievements = extract_achievements(wiki_content)
    moments = extract_key_moments(wiki_content)
    summary = extract_summary(wiki_content)
    archetype = determine_archetype(traits, field)
    era = determine_era(wiki_content)
    working_style = extract_working_style(wiki_content, name)

    # Quality check - need sufficient content
    if len(summary) < 100 or len(achievements) < 20:
        return None

    return {
        "name": name,
        "field": field,
        "subfield": subfield,
        "traits": traits,
        "archetype": archetype,
        "era": era,
        "achievements": achievements,
        "summary": summary,
        "moments": moments,
        "working_style": working_style,
        "raw_length": len(wiki_content)
    }

def save_progress(scientists: list, filename: str = "scientist_db_progress.json"):
    """Save progress to file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(scientists, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(scientists)} scientists to {filename}")

def load_progress(filename: str = "scientist_db_progress.json") -> list:
    """Load progress from file"""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Expose the scientist list for external access
def get_scientist_list():
    return UNIQUE_SCIENTISTS

if __name__ == "__main__":
    print(f"Ready to process {len(UNIQUE_SCIENTISTS)} scientists")
    print("\nFirst 10 scientists to fetch:")
    for s in UNIQUE_SCIENTISTS[:10]:
        print(f"  - {s['name']} ({s['field']}/{s['subfield']})")
