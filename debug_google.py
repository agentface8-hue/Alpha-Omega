import os
from config.settings import settings
import google.generativeai as genai

def test_google_key():
    key = settings.GOOGLE_API_KEY
    if not key:
        print("ERROR: GOOGLE_API_KEY is missing.")
        return

    print(f"Key loaded: {key[:10]}...{key[-5:]}")
    
    genai.configure(api_key=key)
    
    print("Listing available models...")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
        
        print("\nTesting generation with gemini-1.5-flash...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello")
        print("Success! Response:", response.text)
        
    except Exception as e:
        print("\nAPI Error:", e)

if __name__ == "__main__":
    test_google_key()
