from google import genai

GEMINI_API_KEY = "AIzaSyBXxd98NlELKmPkE4swJIq62jJqeGSD74c"

try:
    client = genai.Client(api_key=GEMINI_API_KEY)

    for model in client.models.list():
        print(model.name)

except Exception as e:
    print(f"❌ Error aaya: {e}")