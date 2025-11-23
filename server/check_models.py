"""
Script to list available Gemini models
"""
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure API
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key or api_key == 'your_api_key_here':
    print("❌ Please set your GOOGLE_API_KEY in the .env file")
    exit(1)

genai.configure(api_key=api_key)

print("Available Gemini models that support generateContent:\n")
print("-" * 60)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✓ {model.name}")
        print(f"  Display name: {model.display_name}")
        print(f"  Description: {model.description}")
        print()

print("-" * 60)
print("\nUse one of these model names in api.py")
