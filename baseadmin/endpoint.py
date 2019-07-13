import logging

logger = logging.getLogger(__name__)

import sys
import requests
import json
import uuid
import bcrypt
import time
from functools import wraps
import dateutil.parser
import datetime
import signal

import warnings
warnings.simplefilter("ignore")

import engineio as eio
import socketio as sio

import warnings
warnings.simplefilter("ignore")

from baseadmin                             import config
from baseadmin.storage                     import db
from baseadmin.backend.repositories.client import Client

publish_location = False

def generate_location():
  return "https://{0}:8001".format(config.client.ip)

# override EngineIoClient to allow for unverified SSL connections
# see: https://github.com/miguelgrinberg/python-engineio/issues/99

import ssl
import websocket
import engineio

class MyEngineIoClient(eio.Client):
  def _send_request(self, method, url, headers=None, body=None):
    if self.http is None:
      self.http = requests.Session()
    try:
      # added timeout to ensure that this doesn't endlessly block
      # https://github.com/miguelgrinberg/python-engineio/issues/127
      wait_for = 10 if method == "POST" else 45
      return self.http.request(method, url, timeout=wait_for, headers=headers, data=body, verify=False)
    except requests.exceptions.Timeout:
      self.logger.warn("{0} request to {1} timed out after {2}".format(
        method, url, wait_for
      ))
    except requests.exceptions.ConnectionError:
      pass

  def _connect_websocket(self, url, headers, engineio_path):
      """Establish or upgrade to a WebSocket connection with the server."""
      if websocket is None:  # pragma: no cover
          # not installed
          self.logger.warning('websocket-client package not installed, only '
                              'polling transport is available')
          return False
      websocket_url = self._get_engineio_url(url, engineio_path, 'websocket')
      if self.sid:
          self.logger.info(
              'Attempting WebSocket upgrade to ' + websocket_url)
          upgrade = True
          websocket_url += '&sid=' + self.sid
      else:
          upgrade = False
          self.base_url = websocket_url
          self.logger.info(
              'Attempting WebSocket connection to ' + websocket_url)
      try:
          ws = websocket.create_connection(
              websocket_url + self._get_url_timestamp(),
              header=headers,
              sslopt={"cert_reqs": ssl.CERT_NONE},
              timeout=60
          )
      except ConnectionError:
          if upgrade:
              self.logger.warning(
                  'WebSocket upgrade failed: connection error')
              return False
          else:
              raise engineio.exceptions.ConnectionError('Connection error')
      if upgrade:
          p = engineio.packet.Packet(engineio.packet.PING, data='probe').encode()
          try:
              ws.send(p)
          except Exception as e:  # pragma: no cover
              self.logger.warning(
                  'WebSocket upgrade failed: unexpected send exception: %s',
                  str(e))
              return False
          try:
              p = ws.recv()
          except Exception as e:  # pragma: no cover
              self.logger.warning(
                  'WebSocket upgrade failed: unexpected recv exception: %s',
                  str(e))
              return False
          pkt = engineio.packet.Packet(encoded_packet=p)
          if pkt.packet_type != engineio.packet.PONG or pkt.data != 'probe':
              self.logger.warning(
                  'WebSocket upgrade failed: no PONG packet')
              return False
          p = engineio.packet.Packet(engineio.packet.UPGRADE).encode()
          try:
              ws.send(p)
          except Exception as e:  # pragma: no cover
              self.logger.warning(
                  'WebSocket upgrade failed: unexpected send exception: %s',
                  str(e))
              return False
          self.current_transport = 'websocket'
          self.logger.info('WebSocket upgrade was successful')
      else:
          try:
              p = ws.recv()
          except Exception as e:  # pragma: no cover
              raise engineio.exceptions.ConnectionError(
                  'Unexpected recv exception: ' + str(e))
          open_packet = engineio.packet.Packet(encoded_packet=p)
          if open_packet.packet_type != engineio.packet.OPEN:
              raise engineio.exceptions.ConnectionError('no OPEN packet')
          self.logger.info(
              'WebSocket connection accepted with ' + str(open_packet.data))
          self.sid = open_packet.data['sid']
          self.upgrades = open_packet.data['upgrades']
          self.ping_interval = open_packet.data['pingInterval'] / 1000.0
          self.ping_timeout = open_packet.data['pingTimeout'] / 1000.0
          self.current_transport = 'websocket'

          self.state = 'connected'
          engineio.client.connected_clients.append(self)
          self._trigger_event('connect', run_async=False)
      self.ws = ws

      # start background tasks associated with this client
      self.ping_loop_task = self.start_background_task(self._ping_loop)
      self.write_loop_task = self.start_background_task(self._write_loop)
      self.read_loop_task = self.start_background_task(
          self._read_loop_websocket)
      return True



class MySocketIoClient(sio.Client):
  def _engineio_client_class(self):
    return MyEngineIoClient

socketio = MySocketIoClient()

me = Client(config.client.name, db.state)

# queue-base sending

def send(event, info):
  me.queue.append({ "event": event, "info": info})
  if len(me.queue) == 1: emit_next()

def emit_next():
  if not me.connected: return
  try:
    message = me.queue.get()
    logger.info("sending {0}".format(message))
    socketio.emit(message["event"], message["info"], callback=ack)
  except Exception as e:
    logger.exception(e)
    logger.error("couldn't emit next message, removing it from queue...")
    logger.error("message was: {0}".format(message))
    me.queue.pop()

def ack(feedback=None):
  with me.lock:
    message = me.queue.get()
    logger.info("ack {0} / {1}".format(message, feedback) )
    me.queue.pop()
    if not me.queue.empty: emit_next()

# event handlers

@socketio.on("connect")
def on_connect():
  logger.info("connected")
  me.sid = socketio.eio.sid
  if publish_location:
    location = generate_location()
    logger.info("sending location: {0}".format(location))
    socketio.emit("location", location)
  socketio.emit("refresh", feedback()) # send refresh of state on connect
  if not me.queue.empty: emit_next()

@socketio.on("error")
def on_error(msg):
  logger.info(msg)

@socketio.on("disconnect")
def on_disconnect():
  logger.info("disconnected")
  me.sid = None
  socketio.disconnect()

@socketio.on("release")
def on_release(_):
  logger.info("release: clearing master registration")
  db.config.delete_one({"_id": "master"})
  socketio.disconnect()

@socketio.on("ping2")
def on_ping(request):
  logger.info("ping")
  socketio.emit("pong2", request)

@socketio.on("schedule")
def on_schedule(cmd):
  logger.info("received scheduled cmd: {0}".format(cmd))
  try:
    cmd["schedule"] = dateutil.parser.parse(cmd["schedule"]).timestamp()
    now = datetime.datetime.utcnow().timestamp()
    logger.info("now={0} / schedule={1} / eta={2}".format(now, cmd["schedule"], cmd["schedule"]-now))
    me.schedule.add(cmd)
  except Exception as e:
    feedback(failure=str(e))
  return feedback()

commands = {}

def perform_scheduled_tasks():
  while True:
    try:
      scheduled = me.schedule.get()
      while scheduled and scheduled["schedule"] <= datetime.datetime.utcnow().timestamp():
        logger.info("performing scheduled cmd: {0}".format(scheduled) )
        commands[scheduled["cmd"]](scheduled["args"])
        me.schedule.pop()
        send("performed", feedback(performed=scheduled))
        scheduled = me.schedule.get()
        socketio.sleep(0.05)
    except Exception as e:
      pass
    socketio.sleep(0.05)

socketio.start_background_task(perform_scheduled_tasks)

# command decorator

def feedback(*args, **kwargs):
  # logger.info("state: {0} + {1}".format(me.state, me.schedule.items))
  feedback = {
    "name": me.name,
    "state" : {
      "current" : me.state,
      "futures" : me.schedule.items
    }
  }
  feedback.update(kwargs)
  feedback.update({ "feedback" : args })
  return feedback

def command(cmd):
  def decorator(f):
    commands[cmd] = f
    @wraps(f)
    @socketio.on(cmd)
    def wrapper(data):
      try:
        return feedback(f(data["args"]))
      except Exception as e:
        logger.exception("execution of command failed: {0}".format(str(e)))
      return feedback()
    return wrapper
  return decorator

# register/connection management

def send_registration_request(url, token):
  try:
    response = requests.post(
      url,
      auth=(config.client.name, config.client.secret),
      json={ "token" : token },
      verify=False,
      timeout=60
    )
  except requests.exceptions.ReadTimeout:
    logger.warn("registration: request timed out to {0}".format(url))
    return ( None, None )
  except requests.ConnectionError:
    logger.warn("registration: could not connect to {0}".format(url))
    return ( None, None )
  except Exception as e:
    logger.exception("registration: failed to connect to {0}".format(url))
    return ( None, None )

  # failure
  if response.status_code != requests.codes.ok:
    logger.warn("failed to register: {0}".format(str(response)))
    return ( None, None )

  feedback = response.json()
  logger.debug("feedback: {0}".format(feedback))

  # pending
  if not feedback:
    logger.info("registration is pending")
    return ( "pending", None )

  # rejected
  if feedback["state"] == "rejected":
    logger.warn("registration was rejected")
    return ( "rejected", None )

  # accepted
  logger.info("registration was accepted: {0}".format(feedback["master"]))

  return ("accepted", feedback["master"] )

def register(master, token):
  url = master + "/api/register"
  logger.info("registering at {0} with token {1}".format(url, token))
  while True:
    (outcome, other_master) = send_registration_request(url, token)
    # unsuccessful? bubble back up, unless we're at root, keep trying then
    if outcome == None and master != config.master.root: return None
    if outcome == "rejected": return None # isn't possible right now
    if outcome == "accepted":
      if other_master: # go to redirected master
        result = register(other_master, token)
        if not result is None: return result # bubble up the master
        # failed to register/connect at other master, keep trying with current
      else: # we're at our master
        # store this master and provided token as our current master/token pair
        db.config.update_one( {"_id": "master"},{ "$set" : { "value": master } }, upsert=True )
        db.config.update_one( {"_id": "token"}, { "$set" : { "value": token } },  upsert=True )
        return master # report master
    # if outcome == "pending": pass
    logger.debug("retrying in {0}".format(str(config.master.registration_interval)))
    config.master.registration_interval.sleep()

def connect(master, token):
  if socketio.eio.state == "connected":
    logger.warn("trying to connect while socketio already connected ?")
    return True

  for retry in range(config.master.connection_retries):
    logger.info("connecting to {0} using {1} [try:{2}]".format(master, token, retry+1))
    try:
      socketio.connect(
        master,
        headers={
          "client": config.client.name,
          "token" : token
        })
      return True
    except sio.exceptions.ConnectionError as e:
      if str(e) == "Connection refused by the server":
        logger.warn("can't connect to master ({0}): {1}".format(master, str(e)))
        if retry+1 < config.master.connection_retries:
          logger.debug("retrying connection in {0}".format(str(config.master.connection_interval)))
          config.master.connection_interval.sleep()
        else:
          logger.error("failed to connect after retries")
      else:  # shouldn't really happen anymore ;-) e.g. bad token
        logger.warn("master ({0}) denied connection: {1}".format(master, str(e)))
        socketio.sleep(5) # temp: for case where master still has bad token
        break
  return False

# future implementation of cached configuration interface
def get(key, default=None):
  try:
    return db.config.find_one({"_id": key})["value"]
  except Exception:
    if default:
      db.config.update_one( {"_id": key},{ "$set" : { "value": default } }, upsert=True )
    return default

def run():
  logger.info("starting endpoint event loop...")
  
  token  = get("token", str(uuid.uuid4())) # get or init our unique token
  master = get("master")

  if master is None:
    logger.info("no connecting info, starting registration")
    master = register(config.master.root, token)

  while master:
    while connect(master, token):
      socketio.wait()
      master = get("master")
      if master is None: break
    # can't connect, re-register
    logger.debug("clearing registration")
    db.config.delete_one({"_id": "master"})
    master = register(config.master.root, token)

  logger.fatal("eventloop ended, this shouldn't have happend :-(")
  return False

# temp solution for easier termination of endpoint
def my_teardown_handler(signal, frame):
  socketio.disconnect()
  sys.exit(1)
signal.signal(signal.SIGINT, my_teardown_handler)
