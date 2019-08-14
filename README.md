
This repository provides two apps.
1. telegram-data-miner.py will iterate through a list of channels collecting messages and writing to an S3 bucket.
2. telegram-data.py is a listener for a group of channels waiting for messages.  Messages are written to an S3 bucket.  Future

# Telegram Configuration
Configuration will mostly be through environment variables.  These environment variables contain API Keys, which should no be exposed through code.  So a .env file is stored in an S3 bucket containing the keys and other relevant configuration info.   The name of this S3 bucket is configurable vi the .env found in this github repo.  At startup the program runs settings.py.  This pulls the name of the S3 Bucket containing the environment configuration from the .env found in the current directory.  From this info it then goes and downloads the .env from the S3 bucket containing the full set of runtime environment variables.  A prequeset is to have aws keys setup which have permissions to access the S3 bucket.


Below are the environment variables required.
```
#Telegram Keys
API_ID = 'xxxxxxx'
API_HASH = 'xxxxxxxxxxxxxxxxxxxxxxxxxx'

TELEGRAM_CHANNELS = "tchannels.txt"
TELEGRAM_DATA = "/tmp/telegramData"
TELEGRAM_BUCKET= "osint-telegram-data"
```
- API_ID and API hash are created through telegram.  https://core.telegram.org/api/obtaining_api_id
- TELEGRAM_CHANNELS is the name of the file in containing a list channels to pull messages from.  This file is stored in the same S3 Bucket as the .env file.  File is in csv format and keeps track of the last message read.  New channels added use last message of 1.
```
onepunchman_ep,1
moviesongdrive,713

```
- TELEGRAM_DATA is where the local data is to be stored through processing
- TELEGRAM_BUCKET is the S3 bucket to send the messages too.

