import os
import asyncio
import aiogram
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
#from aiogram.types import ParseMode
from aiogram import F
import aioschedule
import time
from datetime import datetime, timedelta
from pytz import timezone

API_TOKEN = "7850539986:AAEzuGPJYhtw7fQvo5LhPZKzdqIKiU_as2Q"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Расписание событий (пример)
schedule = {}

def main_menu():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Посмотреть расписание", callback_data="show_schedule")],
        [InlineKeyboardButton(text="➕ Добавить событие", callback_data="add_help")],
        [InlineKeyboardButton(text="❌ Удалить событие", callback_data="delete_help")],
    ])
    return kb

def schedule_menu():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить расписание", callback_data="show_schedule")],
        [InlineKeyboardButton(text="➕ Добавить событие", callback_data="add_help")],
        [InlineKeyboardButton(text="❌ Удалить событие", callback_data="delete_help")],
    ])
    return kb

def event_menu():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Посмотреть расписание", callback_data="show_schedule")],
    ])
    return kb


# Функция для отправки уведомлений
async def send_event_notification(event_name, user_id):
    try:
        await bot.send_message(user_id, f"🔔 Напоминание: {event_name}!")
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")

# Фоновая задача для уведомлений
async def schedule_events():
    while True:
        #current_time = time.strftime("%H:%M")
        current_time = str(datetime.now(timezone('Europe/Moscow')).time())[:8]
        if current_time in schedule:
            for event in schedule[current_time][:]:
                await send_event_notification(event['name'], event['user_id'])
                schedule[current_time].remove(event)  # Удаляем после отправки
        await asyncio.sleep(1)

# /start
@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "Привет! Я — бот для работы с расписанием.\n\n"
        "Вот что я умею:",
        reply_markup=main_menu()
    )

# callback кнопки
@dp.callback_query(F.data == "show_schedule")
async def handle_show_schedule(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    output = f"📅 Ваши события {str(datetime.now(timezone('Europe/Moscow')).time())[:8]}:\n\n"
    found = False
    for time_str, events in schedule.items():
        user_events = [e['name'] for e in events if e['user_id'] == user_id]
        if user_events:
            found = True
            output += f"{time_str}:\n"
            for name in user_events:
                output += f" • {name}\n"
    if not found:
        output = "У вас пока нет запланированных событий."
    await callback.message.answer(output,reply_markup=schedule_menu())
    await callback.answer()

@dp.callback_query(F.data == "add_help")
async def handle_add_help(callback: types.CallbackQuery):
    await callback.message.answer("Чтобы добавить событие, напиши:\n\n`/add 12:00:00 Название события`", parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "delete_help")
async def handle_delete_help(callback: types.CallbackQuery):
    await callback.message.answer("Чтобы удалить событие, напиши:\n\n`/delete 12:00:00 Название события`", parse_mode="Markdown")
    await callback.answer()

# /schedule
@dp.message(F.text == "/schedule")
async def show_schedule(message: Message):
    user_id = message.from_user.id
    output = "📅 Ваши события:\n\n"
    found = False
    for time_str, events in schedule.items():
        user_events = [e['name'] for e in events if e['user_id'] == user_id]
        if user_events:
            found = True
            output += f"{time_str}:\n"
            for name in user_events:
                output += f" • {name}\n"
    if not found:
        output = "У вас пока нет запланированных событий."
    await message.answer(output)


@dp.message(F.text == "/ct")
async def show_time(message: Message):
    user_id = message.from_user.id
    output = f"Текуще время: {str(datetime.now(timezone('Europe/Moscow')).time())[:8]}.\n\n"
    await message.answer(output)

# /add 12:00 Название
@dp.message(F.text.startswith("/add"))
async def add_event(message: Message):
    try:
        parts = message.text.split(maxsplit=2)
        time_str = parts[1]
        event_name = parts[2]
        user_id = message.from_user.id

        if time_str not in schedule:
            schedule[time_str] = []

        schedule[time_str].append({'name': event_name, 'user_id': user_id})
        await message.answer(f"✅ Событие «{event_name}» добавлено на {time_str}.",reply_markup=event_menu())
    except Exception:
        await message.answer("❌ Неверный формат. Используйте: `/add 12:00:00 Название события`", parse_mode="Markdown")

# /delete 12:00 Название
@dp.message(F.text.startswith("/delete"))
async def delete_event(message: Message):
    try:
        parts = message.text.split(maxsplit=2)
        time_str = parts[1]
        event_name = parts[2]
        user_id = message.from_user.id

        if time_str in schedule:
            before = len(schedule[time_str])
            schedule[time_str] = [
                event for event in schedule[time_str]
                if not (event['name'] == event_name and event['user_id'] == user_id)
            ]
            after = len(schedule[time_str])

            if before != after:
                await message.answer(f"✅ Событие «{event_name}» удалено с {time_str}.")
            else:
                await message.answer(f"❌ Событие «{event_name}» не найдено.")
        else:
            await message.answer("❌ Нет событий на это время.")
    except Exception:
        await message.answer("❌ Неверный формат. Используйте: `/delete 12:00 Название события`", parse_mode="Markdown")

# Запуск
async def main():
    asyncio.create_task(schedule_events())  # планировщик
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
