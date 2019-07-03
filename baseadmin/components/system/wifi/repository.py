import logging
logger = logging.getLogger(__name__)

from baseadmin.storage import db

def getMap():
  map = {}
  for wifi in db.wifi.find():
    map[wifi["_id"]] = wifi["psk"]
  return map

def getNames():
  return [ wifi["_id"] for wifi in db.wifi.find() ]

def add(ssid, psk):
  db.wifi.insert_one({"_id": ssid, "psk": psk})

def remove(ssid):
  db.wifi.delete_one({"_id": ssid})
