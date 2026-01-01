"""Test Gemini API connection and find correct model name"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY", "")

print("Testing Gemini API...")
genai.configure(api_key=API_KEY)

# Try to list available models
print("\n1. Listing available models:")
try:
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name}")
except Exception as e:
    print(f"  Error listing models: {e}")

# Try different model names
model_names_to_try = [
    'gemini-1.5-flash-latest',
    'gemini-1.5-pro-latest',
    'gemini-pro',
    'models/gemini-1.5-flash-latest',
    'models/gemini-1.5-pro-latest',
]

print("\n2. Testing model names:")
for model_name in model_names_to_try:
    try:
        print(f"\n  Testing: {model_name}")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'Hello'")
        print(f"  ✓ SUCCESS with {model_name}")
        print(f"  Response: {response.text}")
        print(f"\n  USE THIS MODEL: {model_name}")
        break
    except Exception as e:
        print(f"  ✗ Failed: {str(e)[:100]}")
