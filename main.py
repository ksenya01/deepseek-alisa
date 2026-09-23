import os
from fastapi import FastAPI, Request
import requests

app = FastAPI()

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

@app.post("/")
async def main(request: Request):
    body = await request.json()
    user_text = body["request"]["original_utterance"]
        if not user_text or user_text.strip() == "":
        return {
            "version": body["version"],
            "session": body["session"],
            "response": {
                "end_session": False,
                "text": "Привет! Я умный агент на базе DeepSeek. Задайте мне любой вопрос."
            }
        }

    response = requests.post(
        DEEPSEEK_API_URL,
        headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
        json={
            "model": "deepseek-flash",
            "messages": [{"role": "user", "content": user_text}],
            "max_tokens": 150,
        }
    )
    data = response.json()
    if "choices" in data and len(data["choices"]) > 0:
        answer = data["choices"][0].get("message", {}).get("content", "Пустой ответ")
    else:
        answer = f"Ошибка DeepSeek: {data}"

    return {
        "version": body["version"],
        "session": body["session"],
        "response": {
            "end_session": False,
            "text": answer
        }
    }
