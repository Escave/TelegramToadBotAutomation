from telethon import TelegramClient
from telethon import functions
from datetime import datetime, timedelta, date

# Get it from https://my.telegram.org/
API_ID =
API_HASH = ''

BOYS_ID = 1231044699

FEED_TOAD_PERIOD        = timedelta(hours=6, minutes=2)
DEALER_JOB_PERIOD       = timedelta(hours=8, minutes=2)
TOAD_OF_THE_DAY_PERIOD  = timedelta(days=1)

MESSAGES_LIMIT = 100


client = TelegramClient('session_name', API_ID, API_HASH)


def prepare_messages():
    messages = []

    # Toad of the day
    time = datetime.combine(date.today(), datetime.min.time())
    time += timedelta(days=1, minutes=2)
    for i in range(MESSAGES_LIMIT):
        messages.append({'msg': 'жаба дня', 'time': time})
        time += TOAD_OF_THE_DAY_PERIOD

    # Feed the toad
    time = datetime.today() + timedelta(minutes=2)
    for i in range(MESSAGES_LIMIT):
        messages.append({'msg': 'покормить жабу', 'time': time})
        time += FEED_TOAD_PERIOD

    # Dealer job
    time = datetime.today() + timedelta(minutes=2)
    for i in range(MESSAGES_LIMIT):
        messages.append({'msg': 'работа крупье', 'time': time})
        messages.append({'msg': 'завершить работу', 'time': time - timedelta(hours=6)})
        time += DEALER_JOB_PERIOD

    sorted_messages = sorted(messages, key=lambda msg_time: msg_time['time'])

    return sorted_messages[0:MESSAGES_LIMIT]


async def main():
    async for dialog in client.iter_dialogs():
        pass

    entity = await client.get_entity(BOYS_ID)
    messages = prepare_messages()

    for message in messages:
        await client.send_message(entity=entity, message=message['msg'], schedule=message['time'] - timedelta(hours=3))

with client:
    client.loop.run_until_complete(main())