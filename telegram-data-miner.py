import os
import time
from telethon import TelegramClient, sync
import pandas as pd
import settings
import boto3
import tarfile
import shutil

api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
channels_file = os.environ.get('TELEGRAM_CHANNELS')
data_dir = os.environ.get('TELEGRAM_DATA')
count = os.environ.get('TELEGRAM_COUNT')
out_bucket = os.environ.get('TELEGRAM_BUCKET')

#Create working directory
if not os.path.exists(data_dir):
    os.mkdir(data_dir)
    print("Directory " , data_dir,  " Created ")
else:
    print("Directory " , data_dir,  " already exists")

# Download from S3 names list
configBucketName = os.environ.get('S3_CONFIG_BUCKET')
s3 = boto3.resource('s3')
try:
   bucket = s3.Bucket(configBucketName).download_file(channels_file, data_dir+'/'+channels_file)
except botcore.exceptions.ClientError as e:
   if e.response['Error']['Code'] == "404":
      print("The object does not exist.")
   else:
      raise

with open(data_dir+'/'+channels_file, mode='r') as file:
   data = file.readlines()
   client = TelegramClient('session_name', api_id, api_hash).start()
   for row in data:
      print(row)
      group_name = row.rstrip("\n")
      message = client.get_messages(group_name, int(count))
      outfilename=group_name+time.strftime("%Y%m%d-%H%M%S")+'.msq'
      outfile=data_dir+'/'+outfilename
      fo = open(outfile, "w+")
      fo.write(str(message))
      
      # Copy the telegrams to the S3 bucket
      s3.meta.client.upload_file(outfile, out_bucket, outfilename)

# Clean up local versions of tweets.
try:
    shutil.rmtree(data_dir)
except OSError as e:
    print ("Error: %s - %s." % (e.filename, e.strerror))

