import os
from telethon import TelegramClient, sync
import pandas as pd
import settings

api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
channels_file = os.environ.get('TELEGRAM_CHANNELS')
data_dir = os.environ.get('TELEGRAM_DATA')

client = TelegramClient('session_name', api_id, api_hash).start()
group_name = 'webdev_eng'
message = client.get_messages(group_name, 20)
print(message[0])

