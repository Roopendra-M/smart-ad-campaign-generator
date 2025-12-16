import os
import json
import asyncio
import google.generativeai as genai
from .campaign_routes import LOCATIONS, INTERESTS

MODEL_NAME = "gemini-2.5-flash"   # ✅ VALID & FAST


class AIService:
    """Service for AI-powered campaign suggestions using Google Gemini."""

    def __init__(self):
        print("🔥 Initializing AIService with model:", MODEL_NAME)

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not found in environment")

        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(MODEL_NAME)

    async def get_campaign_suggestion(self, business_type=None):
        prompt = self._build_prompt(business_type)

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, lambda: self.client.generate_content(prompt)
            )

            parsed = self._parse_suggestion(response.text)

            # 🔥 CONVERT targeting OBJECT → STRING (FRONTEND SAFE)
            parsed["targeting"] = (
                f"Age: {parsed['age_range']}, "
                f"Location: {parsed['location']}, "
                f"Interests: {', '.join(parsed['interests'])}"
            )

            # Remove helper fields
            parsed.pop("age_range", None)
            parsed.pop("location", None)
            parsed.pop("interests", None)

            return parsed

        except Exception as e:
            print("❌ Gemini API error:", e)
            raise

    def _build_prompt(self, business_type=None):
        interests_list = ", ".join(INTERESTS)
        locations_list = ", ".join(LOCATIONS)

        prompt = f"""
You are an expert marketing strategist.

Return ONLY valid JSON with these fields:
- title
- description
- age_range (example: "18-35")
- location (choose ONE from: {locations_list})
- interests (array of 1–3 values from: {interests_list})
- adText

Rules:
- No explanations
- No markdown
- JSON ONLY
"""

        if business_type:
            prompt += f'\nBusiness Type: "{business_type}"\n'

        return prompt

    def _parse_suggestion(self, text):
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            return json.loads(text[start:end])
        except Exception:
            raise ValueError("Gemini response was not valid JSON")


# ✅ FACTORY (NO SINGLETON, NO CACHING)
def get_ai_service():
    return AIService()
