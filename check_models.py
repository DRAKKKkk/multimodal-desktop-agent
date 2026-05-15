from google import genai

GEMINI_API_KEY = "AIzaSyDhad0s8N89zNny1jL7keaz17Y5Zc7bxFQ"

try:
    client = genai.Client(api_key=GEMINI_API_KEY)

    for model in client.models.list():
        print(model.name)

except Exception as e:
    print(f"❌ Error aaya: {e}")