import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")

if not api_key:
    raise RuntimeError("GROQ_API_KEY is missing from .env")

print("Connecting to Groq...")
print(f"Model: {model}")

client = Groq(api_key=api_key)

response = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "system",
            "content": "You are a concise assistant.",
        },
        {
            "role": "user",
            "content": "Reply with exactly: GROQ CONNECTION SUCCESS",
        },
    ],
    temperature=0,
)

answer = response.choices[0].message.content

print()
print("Groq response:")
print(answer)
print()
print("GROQ SMOKE TEST PASSED")