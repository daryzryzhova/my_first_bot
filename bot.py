import os
from vkbottle.bot import Bot, Message

VK_TOKEN = os.getenv("VK_TOKEN")
if not VK_TOKEN:
    print("Ошибка: VK_TOKEN не задан")
    exit(1)

bot = Bot(VK_TOKEN)

@bot.on.message()
async def handle_message(message: Message):
    await message.answer("Бот работает! Ваше сообщение: " + message.text)

print("Бот запущен и слушает сообщения")
bot.run()
