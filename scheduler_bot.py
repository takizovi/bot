import os
import asyncio
import aiogram
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
#from aiogram.types import ParseMode
from aiogram import F
import aioschedule
import time

API_TOKEN = "7850539986:AAEzuGPJYhtw7fQvo5LhPZKzdqIKiU_as2Q"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Расписание событий (пример)
schedule = {}

# Функция, которая будет отправлять уведомления о событиях
async def send_event_notification(event_name, user_id):
    await bot.send_message(user_id, f"Напоминание: {event_name}!")

# Запланированное событие, которое будет запускать напоминания
async def schedule_events():
    while True:
        # Просматриваем расписание
        for time_str, event_list in schedule.items():
            current_time = time.strftime("%H:%M")
            if current_time == time_str:
                for event in event_list:
                    await send_event_notification(event['name'], event['user_id'])
                    event_list.remove(event)  # Убираем уже выполненное событие
        await asyncio.sleep(60)  # Проверяем каждую минуту

# Обработчик команды /start
@dp.message(F.text == "/start")
async def start(message: Message):
    user_id = message.from_user.id
    await message.answer(f"Привет! Я — бот для работы с расписанием. Напиши /schedule для получения расписания.")

# Обработчик команды /schedule
@dp.message(F.text == "/schedule")
async def show_schedule(message: Message):
    user_id = message.from_user.id
    if not schedule:
        await message.answer("У вас нет запланированных событий.")
    else:
        schedule_str = "Ваши события:\n"
        for time_str, events in schedule.items():
            #if schedule[time_str].user_id == user_id:
                schedule_str += f"{time_str}:\n"
                for event in events:
                    schedule_str += f" - {event['name']}\n"
        await message.answer(schedule_str)

# Обработчик команды /add
@dp.message(F.text.startswith("/add"))
async def add(message: Message):
    try:
        # Формат: /add 12:00 Meeting
        content = message.text.split()
        time_str = content[1]
        event_name = " ".join(content[2:])
        user_id = message.from_user.id
        
        if time_str not in schedule:
            schedule[time_str] = []
        
        schedule[time_str].append({
            'name': event_name,
            'user_id': user_id
        })
        
        await message.answer(f"Событие '{event_name}' добавлено на {time_str} от пользователя {user_id}.")
    except Exception as e:
        await message.answer(f"Ошибка при добавлении события: {str(e)}")





@dp.message(F.text.startswith("/delete"))
async def add(message: Message):
    try:
        # Формат: /add 12:00 Meeting
        content = message.text.split()
        time_str = content[1]
        event_name = " ".join(content[2:])
        user_id = message.from_user.id
        
        if time_str not in schedule:
            schedule[time_str] = []
        
        schedule.remove(schedule[time_str])
        
        await message.answer(f"Событие '{event_name}' удалено с {time_str} от пользователя {user_id}.")
    except Exception as e:
        await message.answer(f"Ошибка при удалении события: {str(e)}")






# Запуск бота и планировщика
async def main():
    # Запускаем планировщик в фоне
    asyncio.create_task(schedule_events())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
