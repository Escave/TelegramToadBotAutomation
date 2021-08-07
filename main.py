from telethon import TelegramClient
from telethon import functions
from datetime import datetime, timedelta, date, time
import pytz

# Get it from https://my.telegram.org/
API_ID = 
API_HASH = ''

CHANNEL_NAME = 'В_айти в windows в бойз'

FEED_TOAD_MSG = "покормить жабу"
FEED_TOAD_PERIOD = timedelta(hours=6, minutes=2)
FEED_TOAD_COUNT = 3

JOB_MSG = "работа крупье"
JOB_PERIOD = timedelta(hours=8, minutes=2)
JOB_COUNT = 3
STOP_JOB_MSG = "завершить работу"
STOP_JOB_DELTA = timedelta(hours=2, minutes=2)

DAY_START = time(0, 1)

TOAD_OF_THE_DAY_MSG = "жаба дня"
TOAD_OF_THE_DAY_COUNT = 3


class Message:
    def __init__(self, text, time):
        self.text = text
        self.datetime = time


client = TelegramClient('session_name', API_ID, API_HASH)


def get_messages(messages, text):
    return [msg for msg in messages if msg.message == text]


def get_last_datetime(messages):
    last_msg = sorted(messages, key=lambda msg: msg.date, reverse=True)

    if not last_msg:
        return None

    return last_msg[0].date


def prepare_messages(scheduled_messages, text, period, min_count):
    messages = get_messages(scheduled_messages, text)

    if len(messages) >= min_count:
        return []

    last_datetime = get_last_datetime(messages)

    empty = False
    if not last_datetime:
        last_datetime = datetime.utcnow()
        empty = True

    new_messages = []

    if empty:
        new_messages.append(Message(text, last_datetime))

    last_datetime += period

    for count in range(min_count - len(messages)):
        new_messages.append(Message(text, last_datetime))
        last_datetime += period

    return new_messages


def prepare_daily_messages(scheduled_messages, text, at_time, min_count):
    messages = get_messages(scheduled_messages, text)

    if len(messages) >= min_count:
        return []

    last_datetime = get_last_datetime(messages)

    empty = False
    if not last_datetime:
        last_datetime = datetime.combine(date.today(), at_time)
        last_datetime = last_datetime.astimezone(pytz.utc)
        empty = True

    new_messages = []

    if empty:
        new_messages.append(Message(text, last_datetime))

    last_datetime += timedelta(days=1)

    for count in range(min_count - len(messages)):
        new_messages.append(Message(text, last_datetime))
        last_datetime += timedelta(days=1)

    return new_messages


def add_pairs(messages, text, time_delta):
    new_messages = []

    for message in messages:
        new_messages += [Message(text, message.datetime + time_delta)]

    messages += new_messages


async def main():
    async for dialog in client.iter_dialogs():
        pass

    dialogs = await client.get_dialogs()
    entity = [await client.get_entity(dialog) for dialog in dialogs if dialog.name == CHANNEL_NAME][0]

    scheduled_messages = (await client(functions.messages.GetScheduledHistoryRequest(peer=entity, hash=0))).messages

    new_messages = []
    new_messages += prepare_daily_messages(scheduled_messages, TOAD_OF_THE_DAY_MSG, DAY_START, TOAD_OF_THE_DAY_COUNT)
    new_messages += prepare_messages(scheduled_messages, FEED_TOAD_MSG, FEED_TOAD_PERIOD, FEED_TOAD_COUNT)

    job_messages = []
    job_messages += prepare_messages(scheduled_messages, JOB_MSG, JOB_PERIOD, JOB_COUNT)
    add_pairs(job_messages, STOP_JOB_MSG, STOP_JOB_DELTA)
    new_messages += job_messages

    for message in new_messages:
        await client.send_message(entity=entity, message=message.text, schedule=message.datetime)

with client:
    client.loop.run_until_complete(main())
