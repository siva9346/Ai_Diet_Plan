import google.generativeai as genai
from dotenv import load_dotenv
import os 

# ✅ Load environment variables from .env (if exists)
load_dotenv()

# ✅ Read Google API key
api_key = os.getenv("GOOGLE_API_KEY")
print("API Key: ", api_key)

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found. Please set your Gemini API key in environment variables.")

# ✅ Force configuration with API key (not ADC)
genai.configure(api_key=api_key)

print("✅ Gemini API configured successfully.")
print("🔍 Fetching available models...\n")

try:
    models = list(genai.list_models())
    print("Models: ", models)
    if not models:
        print("⚠️ No models found for this API key.")
    else:
        for i, model in enumerate(models, 1):
            print(f"{i}. {model.name}")
            print(f"   Supported methods: {model.supported_generation_methods}\n")
            with open("models.txt", "a") as f:
                f.write(f"{i}. {model.name}\n")
                f.write(f"   Supported methods: {model.supported_generation_methods}\n")
                

    print("✅ Model listing completed successfully.")

except Exception as e:
    print(f"❌ Failed to list models: {e}")