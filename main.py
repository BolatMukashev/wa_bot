from fastapi import FastAPI, Request
import uvicorn
import requests
from config import wa_url
from GPT import send_request


app = FastAPI()


def send_message(phone, message):
    payload = {
        "chatId": f"{phone}@c.us",
        "message": f"{message}",
    }
    response = requests.post(wa_url, json=payload)
    print(response.text.encode("utf8"))


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.post("/webhook")
async def green_api_webhook(request: Request):
    body = await request.json()

    type_webhook = body.get("typeWebhook")

    if type_webhook == "incomingMessageReceived":
        sender_data = body.get("senderData", {})

        sender = sender_data.get("sender", "")
        phone = sender.split("@")[0]

        name = sender_data.get("senderName") or sender_data.get("chatName", "")

        message_data = body.get("messageData", {})

        # Текстовое сообщение
        user_text = (
            message_data
            .get("textMessageData", {})
            .get("textMessage")
        )

        # Если не текст — сообщаем пользователю
        if not user_text:
            msg_type = message_data.get("typeMessage", "unknown")
            print(f"📎 Получен нетекстовый тип: {msg_type} от {phone}")
            send_message(phone, "Извините, я пока умею отвечать только на текстовые сообщения.")
            return {"status": "ok"}

        print(f"📩 Новое сообщение от: {phone} (имя: {name}), сообщение: {user_text}")

        answer = send_request(user_text, phone)
        print(f"📩 Ответ ассистента: {answer}")
        
        send_message(phone, answer)

    return {"status": "ok"}


# Запуск: uvicorn main:app --reload
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)