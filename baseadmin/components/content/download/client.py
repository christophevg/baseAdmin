import logging
logger = logging.getLogger(__name__)

import os
import time
from random import randint
from os import listdir
from os.path import isfile, join

try:
  from urllib.parse import urlparse
except ImportError:
  from urlparse import urlparse
  
from ftplib import FTP

from baseadmin.endpoint import me, command, socketio, send, feedback

ROOT = os.environ.get("FILES_ROOT")
if not ROOT: ROOT = "client_files/"

@command("addFile")
def on_add_file(args):
  current = me.state
  if not "files" in current: current["files"] = []
  current["files"].append({
    "name": args["name"],
    "url" : args["url"],
    "size": 0,
    "time": 0
  })
  me.state = current

@command("removeFile")
def on_remove_file(args):
  try:
    current = me.state
    if not "files" in current: current["files"] = []
    logging.info(args["name"])
    logging.info(current["files"])
    current["files"] = [x for x in current["files"] if x["name"] != args["name"]]
    logging.info(current["files"])
    me.state = current
    os.remove(os.path.join(ROOT, args["name"]))
  except:
    logger.warn("deleted not existing file: {0}".format(args["name"]))

def list_files():
  files = {}
  try:
    for fname in listdir(ROOT):
      file = join(ROOT, fname)
      if isfile(file):
        files[fname] = size(file)
  except OSError as e:
    logger.error("can't access files @ " + ROOT + ": " + str(e))
  return files

def import_existing_files():
  new_files = False
  current = me.state
  if not "files" in current: current["files"] = []
  for name, size in list_files().items():
    
    if not next((item for item in current["files"] if item["name"] == name), None):
      new_files = True
      current["files"].append({
        "name"    : name,
        "success" : True,
        "url"     : "",
        "size"    : size,
        "expected": size,
        "time"    : 0
      })

  if new_files:
    me.state = current
    send("performed", feedback(performed="index"))

def download_missing_files():
  current = me.state
  for item in current["files"]:
    if not "success" in item or not item["success"]:
      try:
        result = download(item["name"], item["url"])
        result["success"] = True
        item.update(result)
        try: del item["failure"]
        except: pass
        me.state = current
        send("performed", feedback(performed="download"))
      except Exception as e:
        logger.error("failed to download: {0}".format(str(e)))
        logger.exception(e)
        item["success"] = False
        item["failure"] = str(e)
        me.state = current
        send("failure", feedback())

def download(lname, url):
  logger.info("downloading {0} from {1}".format(lname, url))
  remote = urlparse(url)
  try:
    return {
      "ftp": download_ftp
    }[remote.scheme](lname, os.path.join(ROOT, lname), remote)
  except KeyError:
    raise ValueError("unsupported: {0}".format(remote.scheme))
    
def download_ftp(lname, lpath, remote):
  rname = os.path.basename(remote.path)
  ftp = FTP()
  if remote.port:
    ftp.connect(remote.hostname, remote.port)
  else:
    ftp.connect(remote.hostname)
  ftp.login()
  ftp.voidcmd("TYPE I")
  rsize = ftp.size(rname)
  lsize = size(lpath)
  logger.debug("{0}:{1} / {2}:{3}".format(rname, rsize, lname, lsize))
  start = 0
  if lsize != rsize:
    start = time.time()
    ftp.retrbinary("RETR " + rname, open(lpath, "wb").write)
    lsize = size(lpath)
    logger.debug("downloaded {0}: {1}".format(lpath, lsize))
  ftp.quit()

  return {
    "size"     : lsize,
    "expected" : rsize,
    "time"     : time.time() - start
  }

def size(f):
  try:
    statinfo = os.stat(f)
    return statinfo.st_size
  except Exception as e:
    logger.warn("failed to state {0}: {1}".format(f, str(e)))
  return -1

def sync():
  while True:
    import_existing_files()
    download_missing_files()
    socketio.sleep(30 + randint(0, 9))

socketio.start_background_task(sync)
