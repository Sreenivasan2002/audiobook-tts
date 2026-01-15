from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

key = os.getenv("OPENAI_API_KEY")
print("Key length:", len(key) if key else "Not loaded")

client = OpenAI(api_key=key)

try:
    # Simple working test: retrieve a single model
    model = client.models.retrieve("gpt-4o-mini")
    print("SUCCESS! API key is valid.")
    print("Model ID:", model.id)
except Exception as e:
    print("API call failed:", str(e))