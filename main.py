import os
from fastapi import FastAPI, Request
import requests

app = FastAPI()
@app.get("/health")
async def health():
    return {"status": "ok"}

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

@app.post("/")
async def main(request: Request):
    body = await request.json()
    user_text = body["request"]["original_utterance"]
    session_state = body["state"].get("session", {})

    # Если запрос пустой — приветствие
    if not user_text or user_text.strip() == "":
        return {
            "version": body["version"],
            "session": body["session"],
            "response": {
                "end_session": False,
                "text": "Привет! Я умный агент на базе DeepSeek. Задайте мне любой вопрос."
            },
            "session_state": {}
        }

    # Если это первый запрос пользователя — отвечаем "Секунду..." и просим повторить
    if not session_state.get("waiting"):
        return {
            "version": body["version"],
            "session": body["session"],
            "response": {
                "end_session": False,
                "text": "Секунду, уточняю у DeepSeek..."
            },
            "session_state": {"waiting": True, "question": user_text}
        }

    # Второй запрос — берём сохранённый вопрос и идём в DeepSeek
    question = session_state.get("question", user_text)

    response = requests.post(
        DEEPSEEK_API_URL,
        headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
        json={
            "model": "deepseek-flash",
            "messages": [{"role": "user", "content": question}],
            "max_tokens": 150,
        },
        timeout=10,
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
        },
        "session_state": {}
    }
        }
    }
