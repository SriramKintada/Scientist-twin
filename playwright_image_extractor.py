"""
Automated og:image extractor using Playwright
Systematically extracts Wikipedia og:image URLs for all missing scientists
"""

import json
import asyncio
from playwright.async_api import async_playwright

# Load scientists database
with open('scientist_db_rich.json', 'r', encoding='utf-8') as f:
    scientists = json.load(f)

# Get scientists without images
missing_images = [s for s in scientists if not s.get('image_url')]

print("=" * 70)
print("PLAYWRIGHT OG:IMAGE BATCH EXTRACTOR")
print("=" * 70)
print(f"Scientists missing images: {len(missing_images)}")
print()

async def extract_og_image(page, name):
    """Extract og:image from Wikipedia page"""
    try:
        # Construct Wikipedia URL
        wiki_name = name.replace(" ", "_")
        url = f"https://en.wikipedia.org/wiki/{wiki_name}"

        # Navigate to page
        await page.goto(url, wait_until='domcontentloaded', timeout=15000)

        # Extract og:image meta tag
        og_image = await page.evaluate('''() => {
            const meta = document.querySelector('meta[property="og:image"]');
            return meta ? meta.getAttribute('content') : null;
        }''')

        return og_image
    except Exception as e:
        print(f"    Error: {e}")
        return None

async def main():
    # Load existing mapping if it exists
    try:
        with open('og_image_mapping.json', 'r', encoding='utf-8') as f:
            image_mapping = json.load(f)
        print(f"Loaded {len(image_mapping)} existing image URLs")
        print()
    except FileNotFoundError:
        image_mapping = {}

    no_image = []
    errors = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for idx, scientist in enumerate(missing_images[40:], 41):  # Process remaining (41-75)
            name = scientist['name']
            print(f"{idx}. {name}")
            print(f"   Fetching...", end=" ")

            og_image = await extract_og_image(page, name)

            if og_image:
                image_mapping[name] = og_image
                print("FOUND")
            else:
                no_image.append(name)
                print("NO_IMAGE")

            # Rate limiting
            await asyncio.sleep(0.5)

        await browser.close()

    # Save results
    with open('og_image_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(image_mapping, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print(f"Images found: {len(image_mapping)}")
    print(f"No image: {len(no_image)}")
    print(f"Errors: {len(errors)}")
    print("=" * 70)

    if image_mapping:
        print("\nFound images for:")
        for name in list(image_mapping.keys())[:10]:
            print(f"  - {name}")
        if len(image_mapping) > 10:
            print(f"  ... and {len(image_mapping)-10} more")

    if no_image:
        print(f"\nNo images for:")
        for name in no_image[:10]:
            print(f"  - {name}")
        if len(no_image) > 10:
            print(f"  ... and {len(no_image)-10} more")

    print(f"\nMapping saved to: og_image_mapping.json")

if __name__ == "__main__":
    asyncio.run(main())
