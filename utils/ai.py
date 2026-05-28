import os
import time
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def safe_generate(prompt: str, retries: int = 5) -> str:
    for attempt in range(retries):
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return response.text

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2 + attempt * 2)

    return "⚠️ AI temporarily unavailable."