from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

supabase = create_client(url, key)

# Check random scientists
result = supabase.table('scientists').select('name, image_url').limit(5).execute()
print('Sample of scientists with images:')
print('='*70)
for scientist in result.data:
    img_preview = scientist['image_url'][:50] + '...' if len(scientist['image_url']) > 50 else scientist['image_url']
    print(f"{scientist['name']}: {img_preview}")
print('='*70)

# Count total with images
all_result = supabase.table('scientists').select('name, image_url').execute()
with_images = sum(1 for s in all_result.data if s.get('image_url'))
print(f'\nTotal scientists: {len(all_result.data)}')
print(f'Scientists with images: {with_images}')
print(f'Coverage: {100 * with_images // len(all_result.data)}%')
