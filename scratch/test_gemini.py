import httpx
import sys

def test_key():
    api_key = "AQ.Ab8RN6I8-4mcLuBnKgbKfhyrqHo8w--XPweYjmrKCa7Sqx-nPQ"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    try:
        response = httpx.post(
            url,
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": "Say 'hello'"}]}]}
        )
        print("Status Code:", response.status_code)
        if response.status_code == 200:
            print("Response:", response.json()["candidates"][0]["content"]["parts"][0]["text"])
            print("API Key works!")
        else:
            print("Error Response:", response.text)
    except Exception as e:
        print("Exception:", e)

if __name__ == "__main__":
    test_key()
