import os
import requests
import google.generativeai as genai
from vkbottle.bot import Bot, Message

# --- ПОЛУЧАЕМ ПЕРЕМЕННЫЕ ИЗ ОКРУЖЕНИЯ (BotHost) ---
VK_TOKEN = os.getenv("vk1.a.ui3T60loNchKtKizUdAzn6SeXNR0mndCHKxuCunGP59ZMbVn9mEEmwjJNxONJL6sKarSertfMZGaIj7rqS1uxK90AcHIWmh6npeBtIqBwQYm7KeE0WbLtLuZEmB9ixLxUfPfW1CSx1hTwP8abjgiAia3M6XJ3uX6KbZKaCLLVDF0c1Dzf381p1VXycf8imQbFYRkoYTMvMGC_Tlshw_lsw")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OWNER_ID = int(os.getenv("362359566", 0))  # если не задано, будет 0

if not VK_TOKEN or not GEMINI_API_KEY or not OWNER_ID:
    print("Ошибка: не заданы все переменные окружения!")
    exit(1)

# --- НАСТРАИВАЕМ GEMINI ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")  # можно заменить на gemini-1.5-pro

# --- СОЗДАЁМ БОТА ---
bot = Bot(VK_TOKEN)

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
   Например: "Может быть, вам также понадобится [дополнительный товар]?"
8. Отвечай на русском языке, грамотно и без ошибок.

Ты — лицо компании, будь профессионален!
"""

# --- ФУНКЦИЯ ДЛЯ ОТПРАВКИ УВЕДОМЛЕНИЯ ВЛАДЕЛЬЦУ ---
async def notify_owner(order_text: str):
    """Отправляет сжатый отчёт о заказе владельцу группы."""
    message_text = f"🔔 НОВЫЙ ЗАКАЗ!\n\n{order_text}"
    await bot.api.messages.send(
        peer_id=OWNER_ID,
        message=message_text,
        random_id=0
    )

# --- ОБРАБОТЧИК СООБЩЕНИЙ ---
@bot.on.message()
async def handle_message(message: Message):
    user_text = message.text
    user_id = message.from_id

    # 1. Отправляем запрос в Gemini
    try:
        full_prompt = f"{SYSTEM_PROMPT}\n\nСообщение пользователя: {user_text}\n\nТвой ответ:"
        response = model.generate_content(full_prompt)
        ai_answer = response.text

        # 2. Отправляем ответ пользователю
        await message.answer(ai_answer)

        # 3. Проверяем, не заказ ли это
        if "заказ принят" in ai_answer.lower() or "передам менеджеру" in ai_answer.lower():
            # Отправляем уведомление владельцу
            await notify_owner(
                f"Клиент: vk.com/id{user_id}\n"
                f"Сообщение: {user_text}\n"
                f"Ответ бота: {ai_answer}"
            )

    except Exception as e:
        # Если Gemini не ответил — отправляем запасной ответ
        await message.answer("Извините, я сейчас перегружен. Попробуйте написать чуть позже.")
        print(f"Ошибка Gemini: {e}")

# --- ЗАПУСК БОТА ---
bot.run()
