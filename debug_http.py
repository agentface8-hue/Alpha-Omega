import requests
import json
import os
from config.settings import settings

def test_http():
    key = settings.GOOGLE_API_KEY
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": "Hello"}]
        }]
    }
    
    print(f"Testing URL: ...results for key ending in {key[-5:]}")
    
    response = requests.post(url, headers=headers, json=data)
    
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    print(response.text)

if __name__ == "__main__":
    test_http()
