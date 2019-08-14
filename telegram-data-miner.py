import os
import time
from telethon import TelegramClient, sync
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import ChannelParticipantsSearch
from tempfile import NamedTemporaryFile
import settings
import boto3
import tarfile
import shutil
import json
import datetime
import csv

def date_format(message):
    """
    :param message:
    :return:
    """
    if type(message) is datetime:
        return message.strftime("%Y-%m-%d %H:%M:%S")

api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
channels_file = os.environ.get('TELEGRAM_CHANNELS')
data_dir = os.environ.get('TELEGRAM_DATA')
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

# Need to update the names list file to keep track of last message id.  We do this with a temp file
tempfile = NamedTemporaryFile(mode='w', delete=False)
fields = ['name', 'lastId']

# Get the tweets for all the users in the Names list
with open(data_dir+'/'+channels_file, mode='r') as csv_file, tempfile:
   tempDict = csv.DictWriter(tempfile, fieldnames=fields)
   namesDict = csv.DictReader(csv_file, fieldnames=fields)

   client = TelegramClient('session_name', api_id, api_hash).start()
   for row in namesDict:
      group_name = row["name"]
      lastId = int(row["lastId"])
      if(lastId == 1):
         print('lastid=1')
         messages = client.get_messages(group_name, 1)
      else:
         print('lastid='+str(lastId))
         messages = client.get_messages(group_name, min_id=lastId)

      outfilename=group_name+time.strftime("%Y%m%d-%H%M%S")+'.json'
      outfile=data_dir+'/'+outfilename
      fo = open(outfile, "w+")
      maxid=lastId
      for message in messages:
         msgdict = message.to_dict()
         print(msgdict['id'])
         fo.write(json.dumps(msgdict, default=date_format, indent=4))
         id = msgdict['id']
         if(id > maxid):
            maxid = id
      fo.close()
      row["lastId"] = maxid
      tempDict.writerow(row)

      # Copy the telegrams to the S3 bucket
      s3.meta.client.upload_file(outfile, out_bucket, outfilename)

# Copy the temp file to replace the names list with the last updated message id
shutil.move(tempfile.name, data_dir+'/'+channels_file)

# Copy the names list file back to S3
s3.meta.client.upload_file(data_dir+'/'+channels_file, configBucketName, channels_file)


# Clean up local versions of tweets.
try:
    shutil.rmtree(data_dir)
except OSError as e:
    print ("Error: %s - %s." % (e.filename, e.strerror))

