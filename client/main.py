#
# Client-side python app for photoapp, this time working with
# web service, which in turn uses AWS S3 and RDS to implement
# a simple photo application for photo storage and viewing.
#
# Project 02 for CS 310, Spring 2023.
#
# Authors:
#   YOUR NAME
#   Prof. Joe Hummel (initial template)
#   Northwestern University
#   Spring 2023
#

import requests  # calling web service
import jsons  # relational-object mapping

import uuid
import pathlib
import logging
import sys
import os
import base64

from configparser import ConfigParser

import matplotlib.pyplot as plt
import matplotlib.image as img

TEST_USER_ID = 1

###################################################################
#
# classes
#
class User:
  userid: int  # these must match columns from DB table
  email: str
  lastname: str
  firstname: str
  bucketfolder: str


class Asset:
  assetid: int  # these must match columns from DB table
  userid: int
  assetname: str
  bucketkey: str


class BucketItem:
  Key: str      # these must match columns from DB table
  LastModified: str
  ETag: str
  Size: int
  StorageClass: str


###################################################################
#
# prompt
#
def prompt():
  """
  Prompts the user and returns the command number
  
  Parameters
  ----------
  None
  
  Returns
  -------
  Command number entered by user (0, 1, 2, ...)
  """
  print()
  print(">> Enter a command:")
  print("   0 => end")
  print("   1 => stats")
  print("   2 => users")
  print("   3 => assets")
  print("   4 => download")
  print("   5 => download and display")
  print("   6 => bucket contents")
  print("   7 => upload a photo")

  cmd = int(input())
  return cmd


###################################################################
#
# stats
#
def stats(baseurl):
  """
  Prints out S3 and RDS info: bucket status, # of users and 
  assets in the database
  
  Parameters
  ----------
  baseurl: baseurl for web service
  
  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/stats'
    url = baseurl + api

    res = requests.get(url)
    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return
    #
    # deserialize and extract stats:
    #
    body = res.json()
    #
    print("bucket status:", body["message"])
    print("# of users:", body["db_numUsers"])
    print("# of assets:", body["db_numAssets"])

  except Exception as e:
    logging.error("stats() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


###################################################################
#
# users
#
def users(baseurl):
  """
  Prints out all the users in the database
  
  Parameters
  ----------
  baseurl: baseurl for web service
  
  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/users'
    url = baseurl + api

    res = requests.get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return

    #
    # deserialize and extract users:
    #
    body = res.json()
    #
    # let's map each dictionary into a User object:
    #
    users = []
    for row in body["data"]:
      user = jsons.load(row, User)
      users.append(user)
    #
    # Now we can think OOP:
    #
    for user in users:
      print(user.userid)
      print(" ", user.email)
      print(" ", user.lastname, ",", user.firstname)
      print(" ", user.bucketfolder)

  except Exception as e:
    logging.error("users() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
  
###################################################################
#
# assets
#
def assets(baseurl):
  """
  Prints out all the assets in the database
  
  Parameters
  ----------
  baseurl: baseurl for web service
  
  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/assets'
    url = baseurl + api

    res = requests.get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return

    #
    # deserialize and extract assets:
    #
    body = res.json()
    #
    # let's map each dictionary into a Asset object:
    #
    assets = []
    for row in body["data"]:
      asset = jsons.load(row, Asset)
      assets.append(asset)
    #
    # Now we can think OOP:
    #
    for asset in assets:
      print(asset.assetid)
      print(" ", asset.userid)
      print(" ", asset.assetname)
      print(" ", asset.bucketkey)

  except Exception as e:
    logging.error("assets() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

###################################################################
#
# download
#
def download(baseurl, assetid, display=False):
  """
  Download selected asset
  
  Parameters
  ----------
  baseurl: baseurl for web service
  assetid: target asset id
  display: whether to display the item after download
  
  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/download/' + str(assetid)
    url = baseurl + api

    res = requests.get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return

    #
    # deserialize and extract asset:
    #
    body = res.json()
    if body['message'] == "no such asset...":
      print("No such asset...")
      return
    
    asset = Asset()
    asset.userid = body['user_id']
    asset.assetname = body['asset_name']
    asset.bucketkey = body['bucket_key']
    print("userid:", asset.userid)
    print("asset name:", asset.assetname)
    print("bucket key:", asset.bucketkey)

    binary = base64.b64decode(body['data'])
    with open(asset.assetname, "wb") as f:
      f.write(binary)

    print("Downloaded from S3 and saved as '", asset.assetname,"'")

    if display:
      image = img.imread(asset.assetname)
      plt.imshow(image)
      plt.show()
  

  except Exception as e:
    logging.error("download() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
  
###################################################################
#
# bucket
#
def bucket(baseurl, start_after=None):
  """
  Download selected asset
  
  Parameters
  ----------
  baseurl: baseurl for web service
  assetid: target asset id
  display: whether to display the item after download
  
  Returns
  -------
  last_bucket_key: bucket key of the last content in current page
  """

  try:
    #
    # call the web service:
    #
    api = '/bucket'
    url = baseurl + api
    params = {}
    if start_after is not None:
      params['startafter'] = start_after

    res = requests.get(url, params=params)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return None
    
    body = res.json()
    
    if len(body['data']) == 0:
      return None
    
    bucket_items = []
    for row in body["data"]:
      bucket_item = jsons.load(row, BucketItem)
      bucket_items.append(bucket_item)
    
    for bucket_item in bucket_items:
      print(bucket_item.Key)
      print(" ", bucket_item.LastModified)
      print(" ", bucket_item.Size)
    
    return bucket_items[-1].Key


  except Exception as e:
    logging.error("bucket() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

def upload_handle(baseurl):
  # Get info
  print("Enter the file name of the photo>")
  file_name = input()
  if not os.path.exists(file_name):
    print("File not exist")
    return 
  print("Where was the photo taken? A blurry location like 'near Chicago' is also accpetable>")
  formatted_addr = input()

  api = '/upload/'
  url = baseurl + api + str(TEST_USER_ID)

  # Upload file
  # try:
  f = open(file_name, 'rb')
  E = base64.b64encode(f.read())
  S = E.decode()
  f.close()

  body = {'data':S, 'formatted_addr':formatted_addr, "assetname":file_name}
  res = requests.post(url, json=body)
  print(res.text)



#########################################################################
# main
#
print('** Welcome to PhotoApp v2 **')
print()

# eliminate traceback so we just get error message:
sys.tracebacklimit = 0

#
# what config file should we use for this session?
#
config_file = 'photoapp-client-config'

print("What config file to use for this session?")
print("Press ENTER to use default (photoapp-config),")
print("otherwise enter name of config file>")
s = input()

if s == "":  # use default
  pass  # already set
else:
  config_file = s

#
# does config file exist?
#
if not pathlib.Path(config_file).is_file():
  print("**ERROR: config file '", config_file, "' does not exist, exiting")
  sys.exit(0)

#
# setup base URL to web service:
#
configur = ConfigParser()
configur.read(config_file)
baseurl = configur.get('client', 'webservice')

# print(baseurl)

#
# main processing loop:
#
cmd = prompt()

while cmd != 0:
  #
  if cmd == 1:
    stats(baseurl)
  elif cmd == 2:
    users(baseurl)
  elif cmd == 3:
    assets(baseurl)
  elif cmd == 4:
    print("Enter asset id>")
    assetid = int(input())
    download(baseurl, assetid)
  elif cmd == 5:
    print("Enter asset id>")
    assetid = int(input())
    download(baseurl, assetid, True)
  elif cmd == 6:
    last_bucket_key = bucket(baseurl, None)
    while last_bucket_key is not None:
      print("another page? [y/n]")
      another_page = input()
      if another_page == "y":
        last_bucket_key = bucket(baseurl, last_bucket_key)
      else:
        break
  elif cmd == 7:
    upload_handle(baseurl)
  else:
    print("** Unknown command, try again...")
  #
  cmd = prompt()

#
# done
#
print()
print('** done **')
