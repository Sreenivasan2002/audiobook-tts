from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

key = os.getenv("OPENAI_API_KEY")

print("Raw key from env (first 10 chars):", repr(key[:10]) if key else "None")
print("Full key length:", len(key) if key else 0)

if key:
    try:
        client = OpenAI(api_key=key)
        # Test a very small API call
        test_resp = client.models.list(limit=1)
        print("SUCCESS: API key is valid! Test call worked.")
    except Exception as e:
        print("API call failed with error:", str(e))
else:
    print("Key is empty or not loaded.")