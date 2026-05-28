import os
import time
from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def safe_generate(prompt: str, retries: int = 5) -> str:
    """Safely generate AI response with retry logic."""

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            return response.text

        except Exception as error:
            print(f"Gemini API error: {error}")
            time.sleep(2 + attempt * 2)

    return "⚠️ AI is currently overloaded. Please try again later."