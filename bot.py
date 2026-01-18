import asyncio
import socket
import os
import requests

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import asyncio
import platform

async def is_pc_available(ip: str) -> bool:
    system = platform.system().lower()

    if system == "windows":
        cmd = f"ping -n 1 {ip}"
    else:
        cmd = f"ping -c 1 {ip}"

    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL
    )
    await process.communicate()

    return process.returncode == 0
# ==========================
# НАСТРОЙКИ (из окружения)
# ==========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
PC_MAC = os.getenv("PC_MAC")
SERVER_URL = os.getenv("SERVER_URL")

BROADCAST_IP = "255.255.255.255"
WOL_PORT = 9

# ==========================
# Wake-on-LAN
# ==========================

def send_wol(mac):
    mac_bytes = bytes.fromhex(mac.replace(":", ""))
    packet = b"\xff" * 6 + mac_bytes * 16

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(packet, (BROADCAST_IP, WOL_PORT))

# ==========================
# КНОПКИ
# ==========================

def keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⚡️ Включить ПК")],
            [KeyboardButton(text="💻 Статус ПК")]
        ],
        resize_keyboard=True
    )

# ==========================
# ХЕНДЛЕРЫ
# ==========================

async def start(message: types.Message):
    await message.answer(
        "Привет 👋\nУправление ПК:",
        reply_markup=keyboard()
    )

async def handler(message: types.Message):
    if message.text == "⚡️ Включить ПК":
        send_wol(PC_MAC)
        await message.answer(
            "⚡️ Сигнал отправлен\n⏳ Подожди 30–60 секунд и проверь доступность"
        )

    elif message.text == "🔄 Проверить доступность ПК":
        try:
            r = requests.get(SERVER_URL, timeout=3)
            if r.status_code == 200:
                await message.answer("🟢 ПК доступен")
            else:
                await message.answer("⚫️ ПК недоступен")
        except:
            await message.answer("⚫️ ПК недоступен")

# ==========================
# ЗАПУСК
# ==========================

async def main():
    bot = Bot(
        BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()
    dp.message.register(start, Command("start"))
    dp.message.register(handler)

    await dp.start_polling(bot)

if __name__ == "__main__":

    asyncio.run(main())

