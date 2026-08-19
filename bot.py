import os
from vkbottle.bot import Bot, Message

# Токен теперь берётся из переменной окружения VK_TOKEN
VK_TOKEN = os.getenv("VK_TOKEN")
bot = Bot(VK_TOKEN)

@bot.on.message()
async def handle_message(message: Message):
    await message.answer("Ты написал: " + message.text)

bot.run()
