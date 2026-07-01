from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chat(history: list[dict], user_message: str) -> str:
    history.append({"role": "user", "content": user_message})
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful career assistant for students and recruiters."},
            *history
        ]
    )
    reply = response.choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    return reply