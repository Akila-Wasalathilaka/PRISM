import httpx
import sys

def test_key():
    api_key = "HJ1iAfABkZCh1qSdYAZf9HtOSXPkMncv"
    url = "https://api.mistral.ai/v1/chat/completions"
    
    try:
        response = httpx.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json={
                "model": "mistral-small-latest",
                "messages": [{"role": "user", "content": "Say 'hello'"}]
            }
        )
        print("Status Code:", response.status_code)
        if response.status_code == 200:
            print("Response:", response.json()["choices"][0]["message"]["content"])
            print("API Key works!")
        else:
            print("Error Response:", response.text)
    except Exception as e:
        print("Exception:", e)

if __name__ == "__main__":
    test_key()
