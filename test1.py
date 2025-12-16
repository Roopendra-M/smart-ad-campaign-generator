import os
from dotenv import load_dotenv
import google.generativeai as genai

# 🔥 FORCE override Windows env
load_dotenv(override=True)

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found")

print("Using API key:", API_KEY[:6], "****")

genai.configure(api_key=API_KEY)

# ✅ ONLY VALID MODELS
MODEL_NAME = "gemini-2.5-flash"
print("Using model:", MODEL_NAME)

model = genai.GenerativeModel(MODEL_NAME)

prompt = """
Return ONLY valid JSON:
{
  "status": "ok",
  "message": "Gemini model working"
}
"""

try:
    response = model.generate_content(prompt)
    print("\n✅ Gemini Response:")
    print(response.text)
except Exception as e:
    print("\n❌ Gemini Error:")
    print(e)
