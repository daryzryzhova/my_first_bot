import os
from vkbottle.bot import Bot, Message

VK_TOKEN = os.getenv("VK_TOKEN")
if not VK_TOKEN:
    print("Ошибка: не задан VK_TOKEN")
    exit(1)

bot = Bot(VK_TOKEN)

@bot.on.message()
async def handle_message(message: Message):
    await message.answer("Ты написал: " + message.text)

print("Бот запущен и готов к работе!")
bot.run()
