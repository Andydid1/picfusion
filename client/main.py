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
import io

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
  print("   8 => Pico Pico")
  print("   9 => Pico like")

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
# display
#
def display(baseurl, assetid):
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
    fp = io.BytesIO(binary)
    with fp:
      image = img.imread(fp, format='jpg')
      plt.imshow(image)
      # plt.show()
      plt.show(block=False)  # make plt.show() non-blocking
      plt.pause(3)  # pause for a while for the user to see the image
      plt.close()  # close the figure window

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

##########################################################################
##picfusion()
def picfusion(baseurl):
  """
  Browse through the assets in the database
  
  Parameters
  ----------
  baseurl: baseurl for web service
  
  Returns
  -------
  nothing
  """

  try:

    api = '/assets'
    url = baseurl + api

    res = requests.get(url)

    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return


    body = res.json()
    #
    # map
    #
    assets = []
    for row in body["data"]:
      asset = jsons.load(row, Asset)
      assets.append(asset)

    for asset in assets:
      print(asset.assetid)
      print(" ", asset.assetname)

    #
    # Prompt the user to enter the assetid to display the picture
    #
    print("Enter asset id to display the picture>")
    assetid = int(input())
    current_index = next((index for (index, d) in enumerate(assets) if d.assetid == assetid), None)
    
    # download(baseurl, assetid, True)
    display(baseurl, assetid)
    
    # After displaying the picture, 
    #prompt the user to either display the next picture, or the previous picture, or exit
    #
    while True:
      print("Enter 'n' to display the next picture, 'p' to display the previous picture, or 'e' to exit>")
      action = input().strip().lower()
      if action == 'n':
        if current_index < len(assets) - 1:
          current_index += 1
        else:
          print("This is the last picture. Selecting 'n' will take you to the first picture.")
          current_index = 0
      elif action == 'p':
        if current_index > 0:
          current_index -= 1
        else:
          print("This is the first picture. Selecting 'p' will take you to the last picture.")
          current_index = len(assets) - 1
      elif action == 'e':
        break
      else:
        print("Invalid input. Please enter 'n', 'p', or 'e'.")
        continue
      # download(baseurl, assets[current_index].assetid, True)
      display(baseurl, assets[current_index].assetid)

  except Exception as e:
    logging.error("picfusion() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

##########################################################################
##
##
def picfusion_interact(baseurl):
  """
  Browse through the assets in the database
  
  Parameters
  ----------
  baseurl: baseurl for web service
  
  Returns
  -------
  nothing
  """

  try:

    api = '/assets'
    url = baseurl + api

    res = requests.get(url)

    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return


    body = res.json()
    #
    # map
    #
    assets = []
    for row in body["data"]:
      asset = jsons.load(row, Asset)
      assets.append(asset)

    for asset in assets:
      print(asset.assetid)
      print(" ", asset.assetname)
      # Fetch interaction data for the asset
      interaction_url = baseurl + '/interactions/' + str(asset.assetid)
      interaction_res = requests.get(interaction_url)
      if interaction_res.status_code == 200:
        interaction_data = interaction_res.json()
        print("Likes:", interaction_data['interaction_type'])
    #
    # Prompt the user to enter the assetid to display the picture
    #
    print("Enter asset id to display the picture>")
    assetid = int(input())
    current_index = next((index for (index, d) in enumerate(assets) if d.assetid == assetid), None)
    
    # download(baseurl, assetid, True)
    display(baseurl, assetid)
    
    # After displaying the picture, 
    #prompt the user to either display the next picture, or the previous picture, or exit
    #
    while True:
      # print("Enter 'n' to display the next picture, 'p' to display the previous picture, or 'e' to exit>")
      print("Enter 'n' to display the next picture, 'p' to display the previous picture, '1' to like, '2' to dislike, or 'e' to exit>")

      action = input().strip().lower()
      if action == 'n':
        if current_index < len(assets) - 1:
          current_index += 1
        else:
          print("This is the last picture. Selecting 'n' will take you to the first picture.")
          current_index = 0
      elif action == 'p':
        if current_index > 0:
          current_index -= 1
        else:
          print("This is the first picture. Selecting 'p' will take you to the last picture.")
          current_index = len(assets) - 1
      elif action == '1':
            send_interaction(baseurl, assets[current_index].assetid, 1)
      elif action == '2':
            send_interaction(baseurl, assets[current_index].assetid, -1)      
      elif action == 'e':
        break
      else:
        print("Invalid input. Please enter 'n', 'p', '1', '2', or 'e'.")
        continue
      # download(baseurl, assets[current_index].assetid, True)
      display(baseurl, assets[current_index].assetid)

  except Exception as e:
    logging.error("picfusion() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

##########################################################################
## 
def send_interaction(baseurl, assetid, interaction_type):
    """
    Send a POST request to the server to record the user's interaction with an asset.
    
    Parameters
    ----------
    baseurl: baseurl for web service
    assetid: target asset id
    interaction_type: 1 for like, -1 for dislike
    
    Returns
    -------
    nothing
    """
    try:
        api = '/interactions'
        url = baseurl + api
        data = {
            'assetid': assetid,
            'interaction_type': interaction_type
        }
        res = requests.post(url, json=data)
        if res.status_code != 200:
            print("Failed with status code:", res.status_code)
            print("url: " + url)
            if res.status_code == 400:  # we'll have an error message
                body = res.json()
                print("Error message:", body["message"])
    except Exception as e:
        logging.error("send_interaction() failed:")
        logging.error("url: " + url)
        logging.error(e)

#########################################################################
# main
#
print('** Welcome to Picfusion! Pico Pico! **')
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
  elif cmd == 8:
    picfusion(baseurl)
  elif cmd == 9:
    picfusion_interact(baseurl)
  else:
    print("** Unknown command, try again...")
  #
  cmd = prompt()

#
# done
#
print()
print('** done **')
