import os
import json
import urllib.request
import urllib.error
from vkbottle.bot import Bot, Message

# --- ДАННЫЕ ДЛЯ ПОДКЛЮЧЕНИЯ К БИТРИКС24 ---
BITRIX24_WEBHOOK_URL = "https://b24-4d8tl3.bitrix24.ru/rest/1/5ib9m7o5yr3vhei3/"
# -------------------------------------------

# --- ПОЛУЧАЕМ ПЕРЕМЕННЫЕ ИЗ ОКРУЖЕНИЯ (BotHost) ---
VK_TOKEN = os.getenv("VK_TOKEN")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
OWNER_ID = os.getenv("OWNER_ID")

# Проверяем, что все переменные заданы
if not VK_TOKEN:
    print("❌ Ошибка: не задан VK_TOKEN")
    exit(1)
if not YANDEX_API_KEY:
    print("❌ Ошибка: не задан YANDEX_API_KEY")
    exit(1)
if not YANDEX_FOLDER_ID:
    print("❌ Ошибка: не задан YANDEX_FOLDER_ID")
    exit(1)
if not OWNER_ID:
    print("❌ Ошибка: не задан OWNER_ID")
    exit(1)

OWNER_ID = int(OWNER_ID)

# --- СОЗДАЁМ БОТА ---
bot = Bot(VK_TOKEN)
print("✅ Бот создан")

# --- СИСТЕМНЫЙ ПРОМПТ (инструкция для ИИ) ---
SYSTEM_PROMPT = """
Ты — умный помощник-консультант в сообществе ВКонтакте. 
Твоя задача — общаться с клиентами вежливо, дружелюбно и помогать им с заказами.

ПРАВИЛА:
1. Всегда представляйся: "Здравствуйте! Я — ваш виртуальный помощник. Чем могу помочь?"
2. Если клиент спрашивает о товаре/услуге — дай подробную информацию.
3. Если клиент хочет сделать заказ — собери следующие данные:
   - Имя клиента
   - Что именно хочет заказать
   - Контактный телефон (если не указал — попроси)
   - Адрес (если нужна доставка)
4. После того как все данные собраны — скажи: "Спасибо! Ваш заказ принят. Я передам его менеджеру."
5. Если клиент спрашивает о ценах, скидках, доставке — отвечай честно и подробно.
6. Если клиент написал что-то не по теме — вежливо направь его к нужному разделу.
7. В конце каждого диалога предлагай дополнительный товар или услугу (допродажа).
8. Отвечай на русском языке, грамотно и без ошибок.
Ты — лицо компании, будь профессионален!
"""

# --- ФУНКЦИЯ ДЛЯ ЗАПРОСА К YANDEXGPT (через urllib) ---
def ask_yandex_gpt(user_text):
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    
    data = {
        "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": 2000
        },
        "messages": [
            {"role": "system", "text": SYSTEM_PROMPT},
            {"role": "user", "text": user_text}
        ]
    }
    
    json_data = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(
        url,
        data=json_data,
        headers={
            "Authorization": f"Api-Key {YANDEX_API_KEY}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            result = json.loads(response_data)
            return result["result"]["alternatives"][0]["message"]["text"]
    except urllib.error.URLError as e:
        print(f"❌ Ошибка сети: {e}")
        raise
    except Exception as e:
        print(f"❌ Ошибка при запросе к YandexGPT: {e}")
        raise

# --- ФУНКЦИЯ ДЛЯ ОТПРАВКИ УВЕДОМЛЕНИЯ ВЛАДЕЛЬЦУ ---
async def notify_owner(order_text: str):
    try:
        await bot.api.messages.send(
            peer_id=OWNER_ID,
            message=f"🔔 НОВЫЙ ЗАКАЗ!\n\n{order_text}",
            random_id=0
        )
        print("✅ Уведомление отправлено владельцу")
    except Exception as e:
        print(f"❌ Ошибка при отправке уведомления: {e}")

# --- ОБРАБОТЧИК СООБЩЕНИЙ ---
@bot.on.message()
async def handle_message(message: Message):
    user_text = message.text
    user_id = message.from_id
    print(f"📩 Получено сообщение от {user_id}: {user_text}")

    try:
        print("⏳ Отправляю запрос в YandexGPT...")
        ai_answer = ask_yandex_gpt(user_text)
        print("✅ Получен ответ от YandexGPT")

        await message.answer(ai_answer)
        print("✅ Ответ отправлен пользователю")

        if "заказ принят" in ai_answer.lower() or "передам менеджеру" in ai_answer.lower():
            await notify_owner(
                f"Клиент: vk.com/id{user_id}\n"
                f"Сообщение: {user_text}\n"
                f"Ответ бота: {ai_answer}"
            )

    except Exception as e:
        error_msg = f"❌ Ошибка при обработке: {e}"
        print(error_msg)
        await message.answer("Извините, я сейчас перегружен. Попробуйте написать позже.")

# --- ЗАПУСК БОТА ---
print("🚀 Бот запускается...")
bot.run()
