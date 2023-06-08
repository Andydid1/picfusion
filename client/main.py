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
import utils
import hashlib

from configparser import ConfigParser

import matplotlib.pyplot as plt
import matplotlib.image as img

TEST_USER_ID = 1
USER_ID = None

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
  like_count: int
  userid: int
  assetname: str
  bucketkey: str
  formatted_addr: str
  postal_code: int
  city: str
  state: str
  country: str
  latitude: float
  longitude: float


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
  print("   10 => customed display")

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
# assets
#
def assets(baseurl, display=False):
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
      return None

    #
    # deserialize and extract assets:
    #
    body = res.json()
    #
    # let's map each dictionary into a Asset object:
    #
    # print(body['data'])
    assets = []
    for row in body["data"]:
      row = {k: v for k, v in row.items() if v is not None}
      asset = jsons.load(row, Asset)
      asset.like_count = row['like_count']
      assets.append(asset)
    #
    # Now we can think OOP:
    #
    if (display):
      for asset in assets:
        print(asset.assetid)
        print(" UserID: ", asset.userid)
        print(" AssetName:", asset.assetname)
        print(" Likes:", asset.like_count)
        print(" Location:", asset.formatted_addr)

    #   if asset.formatted_addr: print(" ", asset.formatted_addr) 
      # print(" ", asset.bucketkey)
    
    return assets

  except Exception as e:
    logging.error("assets() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return None

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
    print("==== Current Pic ====")
    print("Asset Name:", asset.assetname)

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

def get_location(location):
  try:
    #
    # call the web service:
    #
    api = '/location'
    url = baseurl + api
    params = {'location':location}

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
      return

    body = res.json()
    return body['latitude'], body['longitude']

  except Exception as e:
    logging.error("get_location() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

def sort_handle(asset_lst):
    while True:
      print(">>> Sort By?")
      print(">>> [l]ikes  [d]istance")
      sort_type = input().strip().lower()
      if sort_type == 'l':
        print(">>> [a]scend  [d]escend")
        order = input().strip().lower() == 'd'
        return sorted(asset_lst, key=lambda x: x.like_count, reverse=order)
      elif sort_type == 'd':
        print(">>> Please provide a location (e.g near Chicago):")
        location = input()
        print(">>> [a]scend  [d]escend")
        order = input().strip().lower() == 'a'
        target_latitude, target_longitude = get_location(location)
        return utils.sort_by_geo(asset_lst, target_latitude, target_longitude, order)
      else:
        print("Invalid Sort Type.")
        continue

def display_lst(asset_lst, current_index):
  left = max(0, current_index - 2)
  right = min(len(asset_lst) - 1, max(current_index + 2, 5))
  print("==== Photos ====")
  print ("{:<15} {:<8} {:<15}".format('Name', 'Likes', 'Location'))
  for i in range(left, right+1):
    asset = asset_lst[i]
    output = "{:<15} {:<8} {:<15}".format(asset.assetname, asset.like_count, asset.formatted_addr)
    if i == current_index:
      output += "  <=="
    print(output)

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
    asset_lst = assets(baseurl)
    current_index = 0

    # Main Loop
    while True:
      display_lst(asset_lst, current_index)
      display(baseurl, asset_lst[current_index].assetid)
      print("==== Operations ====")
      print(">>> [n]ext  [p]rev")
      print(">>> [l]ike  [d]islike")
      print(">>> [s]ort  [e]xit")
      action = input().strip().lower()
      if action == 'n':
        if current_index < len(asset_lst) - 1:
          current_index += 1
        else:
          print("[This is the last picture. Selecting 'n' to the first picture.]")
          current_index = 0
      elif action == 'p':
        if current_index > 0:
          current_index -= 1
        else:
          print("[This is the first picture. Selecting 'p' to the last picture.]")
          current_index = len(asset_lst) - 1
      elif action == 'l':
        send_interaction(baseurl, asset_lst[current_index].assetid, 1)
      elif action == 'd':
        send_interaction(baseurl, asset_lst[current_index].assetid, -1)   
      elif action == 's':
        asset_lst = sort_handle(asset_lst)
        current_index = 0
      elif action == 'e':
        break
      else:
        print("Invalid input")
        continue
      # download(baseurl, assets[current_index].assetid, True)

  except Exception as e:
    logging.error("picfusion() failed:")
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
# customed display
def customed_display(baseurl):
    """
    Customized Display

    Parameters
    ----------
    baseurl: baseurl for web service
  
    Returns
    -------
    nothing
    """
    while True:
        print(">> Enter 'ASC' for ascending order, 'DESC' for descending order, or 'e' to exit:")
        order = input().strip().upper()
        if order in ['ASC', 'DESC']:
            display_assets_by_likes(baseurl, order)
        elif order == 'E':
            break
        else:
            print("Invalid input. Please enter 'ASC', 'DESC', or 'e'.")

##########################################################################
# 
#
def display_assets_by_likes(baseurl, order):
    """
    Display assets ordered by likes in ascending or descending order

    Parameters
    ----------
    baseurl: baseurl for web service
    order: str, either 'ASC' or 'DESC'
  
    Returns
    -------
    nothing
    """
    try:
        # Get all assets
        asset_lst = assets(baseurl)

        # Sort assets by like_count
        asset_lst.sort(key=lambda x: x.like_count, reverse=(order == 'DESC'))

        # Display sorted assets
        for asset in asset_lst:
            print(asset.assetid)
            print(" ", asset.assetname)
            print("  Likes:", asset.like_count)

    except Exception as e:
        logging.error("display_assets_by_likes() failed:")
        logging.error(e)
        return
    
#########################################################################
# sign in
def signin(baseurl, email, encrypted_password) -> bool:
  api = '/signin'
  url = baseurl + api

  data = {
    "email": email,
    "password": encrypted_password
    }

  try:
    res = requests.post(url, json=data)
  
    if res.status_code == 201:
      print("Successfully Log in!")
      global USER_ID
      USER_ID = res.json()['userid']
      return True
    else:
      print("Log in failed, status code:", res.status_code)
      print("Error message:", res.json())
      return False
      
  except Exception as e:
    logging.error("signin() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return False
  
  #########################################################################
# register
def register(baseurl, email, username, encrypted_user_password):
  api = '/register'
  url = baseurl + api

  data = {
    "email": email,
    "username": username,
    "password": encrypted_user_password
    }

  try:
    res = requests.post(url, json=data)
  
    if res.status_code == 200:
      print("Successfully Register!")
    else:
      print("Register failed, status code:", res.status_code)
      print("Error message:", res.json())

  except Exception as e:
    logging.error("register() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
  
  #########################################################################
# login prompt
def login_prompt(baseurl):
  logged_in = False
  
  print()
  print("Hello! Welcome to your PicFusion!")
  try:
    while not logged_in:
      print()
      print("   1 => Sign In")
      print("   2 => Rigister as a new user")
      print()
      signinOption = int(input("SignIn or Register: "))
      
      if signinOption == 1:
        email = input("Please Enter your Email: ")
        password = input("Please Enter your Password: ")
        
        encrypted_password = hashlib.md5(password.encode()).hexdigest()
        
        result = signin(baseurl, email, encrypted_password)
        if result:
          logged_in = True

        
      elif signinOption == 2:
        email = input("Please Enter your email: ")
        username = input("Please Enter a User Name: ")
        user_password = input("Please Enter your Password: ")
    
        encrypted_user_password = hashlib.md5(user_password.encode()).hexdigest()
    
        register(baseurl, email, username, encrypted_user_password)
        
  except Exception as e:
    logging.error("register() failed:")
    logging.error(e)
    return



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


###############################
#
# Login process
#

while USER_ID is None:
  login_prompt(baseurl)
###############################

#
# main processing loop:
#
cmd = prompt()

while USER_ID is not None and cmd != 0:
  #
  if cmd == 1:
    stats(baseurl)
  elif cmd == 2:
    users(baseurl)
  elif cmd == 3:
    assets(baseurl, True)
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
  elif cmd == 9:
    picfusion_interact(baseurl)
  elif cmd == 10:
    customed_display(baseurl)
  else:
    print("** Unknown command, try again...")
  #
  cmd = prompt()

#
# done
#
print()
print('** done **')
