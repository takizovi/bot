import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.filters import Command
import aioschedule as schedule
from datetime import datetime, timedelta

API_TOKEN = '8070156187:AAFqOPD5sM0PnKAQG3EnTOscV1h79sN0Rts'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Хранилище событий (в реальности лучше использовать БД)
user_schedules = {}

# Команда /start
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Я бот-расписание. Используй /add чтобы добавить событие и /list чтобы увидеть список.")

# Команда /add
@dp.message(Command("add"))
async def add_event(message: types.Message):
    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            raise ValueError

        time_str, event = parts[1], parts[2]
        event_time = datetime.strptime(time_str, "%H:%M")

        user_id = message.from_user.id
        now = datetime.now()
        event_datetime = now.replace(hour=event_time.hour, minute=event_time.minute, second=0, microsecond=0)
        if event_datetime < now:
            event_datetime += timedelta(days=1)

        if user_id not in user_schedules:
            user_schedules[user_id] = []

        user_schedules[user_id].append((event_datetime, event))
        await message.answer(f"Событие добавлено: {event} в {event_datetime.strftime('%H:%M')}")

    except ValueError:
        await message.answer("Используй формат: /add HH:MM событие")

# Команда /schedule
@dp.message(Command("schedule"))
async def list_events(message: types.Message):
    user_id = message.from_user.id
    events = user_schedules.get(user_id, [])
    if not events:
        await message.answer("У тебя пока нет событий.")
    else:
        msg = "\n".join([f"{dt.strftime('%H:%M')} - {ev}" for dt, ev in sorted(events)])
        await message.answer("Твои события:\n" + msg)

# Проверка и отправка уведомлений
async def notify_events():
    now = datetime.now()
    for user_id, events in list(user_schedules.items()):
        for event in events:
            dt, text = event
            if 0 <= (dt - now).total_seconds() <= 60:
                await bot.send_message(user_id, f"🔔 Напоминание: {text} в {dt.strftime('%H:%M')}")
        # Очищаем прошедшие
        user_schedules[user_id] = [e for e in events if e[0] > now]

# Фоновая задача
async def scheduler():
    schedule.every(1).minutes.do(notify_events)
    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)

# Запуск
async def main():
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
