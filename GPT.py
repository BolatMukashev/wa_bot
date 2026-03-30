from openai import OpenAI
from config import GPT_KEY


client = OpenAI(api_key=GPT_KEY)

# Словарь: phone -> список сообщений (история диалога)
conversation_histories = {}

MAX_HISTORY = 20  # максимум сообщений в истории (не считая system prompt)

instruction = """
Ты помощник копи-центра.
Отвечай всегда коротко и по делу.
Для начала запомни эту информацию:
Название копи-центра "Print Paper".
Расположение: Казахстан, г.Уральск, мкр. Сверо-Восток 2, д.47 (вход со стороны детской площадки).
Время работы: с 10 до 18, без выходных.
Стоимость услуг:
ч/б распечатка или копирование 1 страницы - 40 тг,
двухсторонний лист - 80 тг,
цветная распечатка - 80 тг,
двухсторонняя цветная распечатка - 160 тг,
фото 10х15 см - 60 тг,
фото 13х18 см - 100 тг,
фото А5 - 150 тг,
фото А4 - 200 тг,
фото А3 - 800 тг,
переплет документов - 600 тг,
ламинация А4 - 500 тг,
фото на документы, размеры:
3х4 см (1 или 2 штуки) - нет,
3х4 см (4 штуки) - 600 тг,
3,5х4,5 см (4 штуки) - 750 тг,
5х5 см (2 штуки) - 900 тг
"""


def trim_history(phone):
    """Обрезаем историю, оставляя только MAX_HISTORY последних сообщений."""
    history = conversation_histories[phone]
    system_msg = history[0]  # system prompt всегда остаётся
    rest = history[1:]
    if len(rest) > MAX_HISTORY:
        conversation_histories[phone] = [system_msg] + rest[-MAX_HISTORY:]


def reset_history(phone):
    """Сбрасываем историю пользователя."""
    conversation_histories.pop(phone, None)


def send_request(user_text, phone):
    # Команда сброса истории
    if user_text.strip().lower() in ["/старт", "/reset", "/start", "/сброс"]:
        reset_history(phone)
        return "История очищена. Начнём сначала! Чем могу помочь?"

    # Инициализируем историю для нового пользователя
    if phone not in conversation_histories:
        conversation_histories[phone] = [
            {"role": "system", "content": instruction}
        ]

    # Добавляем сообщение пользователя в историю
    conversation_histories[phone].append(
        {"role": "user", "content": user_text}
    )

    # Обрезаем историю если она слишком длинная
    trim_history(phone)

    # Отправляем всю историю в OpenAI
    response = client.chat.completions.create(
        model="gpt-5.4-nano",
        messages=conversation_histories[phone]
    )

    assistant_message = response.choices[0].message.content

    # Сохраняем ответ ассистента в историю
    conversation_histories[phone].append(
        {"role": "assistant", "content": assistant_message}
    )

    return assistant_message


if __name__ == "__main__":
    test_phone = "77001234567"
    print(send_request("Здравствуйте! Сколько стоит цветная распечатка?", test_phone))
    print(send_request("А двухсторонняя?", test_phone))
    print(send_request("Как вас найти?", test_phone))