import os
import google.generativeai as genai
import json
from dotenv import load_dotenv
from .campaign_routes import LOCATIONS, INTERESTS
import asyncio

# Load environment variables
load_dotenv()

class AIService:
    """Service for AI-powered campaign suggestions using Google Gemini."""

    def __init__(self):
        self.client = None
        self.model_name = "gemini-2.5-pro"  # 🚨 updated model name
        
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Gemini client using API key."""
        api_key = os.getenv("GEMINI_API_KEY")  # 🚨 UPDATED variable name

        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.client = genai.GenerativeModel(self.model_name)
            except Exception as e:
                print(f"Error initializing Gemini client: {e}")
        else:
            print("Gemini API key not found. Please set GEMINI_API_KEY in your .env file.")

    async def get_campaign_suggestion(self, business_type=None):
        """Generate campaign suggestion using Gemini."""

        if not self.client:
            raise ValueError("Gemini client is not initialized. Set GEMINI_API_KEY first.")

        prompt = self._build_prompt(business_type)

        try:
            # Run sync SDK in async loop
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.generate_content(prompt)
            )

            suggestion_text = response.text
            parsed = self._parse_suggestion(suggestion_text)

            if not self._validate_suggestion(parsed):
                raise ValueError("Invalid format from Gemini AI response.")

            return parsed

        except Exception as e:
            print(f"Gemini API error: {e}")
            raise

    def _build_prompt(self, business_type=None):
        """Build the marketing prompt."""

        interests_list = ", ".join(INTERESTS)
        locations_list = ", ".join(LOCATIONS)

        base_prompt = f"""
You are an expert marketing strategist.

Create a JSON response ONLY with these fields:
- title
- description
- targeting (format: "Age: X-Y, Location: [City], Interests: [Interest1, Interest2]")
- adText

Rules:
1. Only choose 1–3 interests from this list: {interests_list}
2. Choose ONE location from this list: {locations_list}
3. Response MUST be valid JSON only — no explanations.

"""

        if business_type:
            base_prompt += f"\nBusiness Type: {business_type}\n"

        return base_prompt

    def _parse_suggestion(self, suggestion_text):
        """Parse JSON output."""
        try:
            start_idx = suggestion_text.find('{')
            end_idx = suggestion_text.rfind('}') + 1
            json_str = suggestion_text[start_idx:end_idx]
            return json.loads(json_str)
        except Exception:
            raise ValueError("Gemini response was not valid JSON")

    def _validate_suggestion(self, suggestion):
        """Ensure required fields exist."""
        return all(k in suggestion for k in ["title", "description", "targeting", "adText"])


# Singleton instance
ai_service = AIService()
