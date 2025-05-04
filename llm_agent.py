import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

def generate_commit_message(prompt: str) -> str:
    try:
        # ✅ contents 直接传入字符串（或 Part 对象）
        response = client.models.generate_content(
            model="gemini-2.0-flash",  # or "gemini-2.0-pro", "gemini-2.0-flash"
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print("❌ Gemini API error:", e)
        return "chore: update code"
