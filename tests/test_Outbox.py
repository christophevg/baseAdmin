import mongomock
import time

from baseadmin.messaging import Outbox

def create_empty_outbox(provided_db=None, timeout=5000):
  db = provided_db or mongomock.MongoClient().db
  return (db, Outbox(db, timeout=timeout))

def test_empty_outbox_has_no_messages():
  (db, outbox) = create_empty_outbox()
  assert outbox.size() == 0

def test_sending_single_message_without_ack():
  (db, outbox) = create_empty_outbox()
  id = outbox.add("topic", "msg 1")
  assert outbox.size(all=True) == 1
  assert outbox.size() == 1
  assert db.outbox.count_documents({}) == 1
  for item in outbox:
    assert item["id"]    == id
    assert item["topic"] == "topic"
    assert item["msg"]   == "msg 1"
    assert item["ack"]   == False
    outbox.sent(item["id"])
  assert outbox.size() == 0
  assert outbox.size(all=True) == 0
  assert db.outbox.count_documents({}) == 0

def test_sending_single_message_with_ack():
  (db, outbox) = create_empty_outbox(timeout=100) # custom timeout
  id = outbox.add("topic", "msg 1", ack=True)
  assert outbox.size(all=True) == 1
  assert outbox.size() == 1
  assert db.outbox.count_documents({}) == 1
  for item in outbox:
    assert item["id"]    == id
    assert item["topic"] == "topic"
    assert item["msg"]   == "msg 1"
    assert item["ack"]   == True
    outbox.sent(item["id"])
  assert outbox.size() == 0
  assert outbox.size(all=True) == 1
  assert db.outbox.count_documents({}) == 1
  time.sleep(0.2) # this ensures that the timeout for the ack has passed
  assert outbox.size() == 1
  outbox.ack(item["id"])
  assert outbox.size() == 0
  assert outbox.size(all=True) == 0
  assert db.outbox.count_documents({}) == 0

def test_multiple_messages_without_ack():
  (db, outbox) = create_empty_outbox()
  outbox.add("topic", "msg 1")
  outbox.add("topic", "msg 2")
  outbox.add("topic", "msg 3")
  assert outbox.size() == 3
  assert db.outbox.count_documents({}) == 3
  for idx, item in enumerate(outbox):
    assert item["msg"] == "msg {0}".format(idx+1)
    outbox.sent(item["id"])
  assert outbox.size() == 0
  assert db.outbox.count_documents({}) == 0

def test_selective_sending_of_messages_without_ack():
  (db, outbox) = create_empty_outbox()
  id1 = outbox.add("topic", "msg 1")
  id2 = outbox.add("topic", "msg 2")
  id3 = outbox.add("topic", "msg 3")
  id4 = outbox.add("topic", "msg 4")
  id5 = outbox.add("topic", "msg 5")
  assert outbox.size() == 5
  assert db.outbox.count_documents({}) == 5
  outbox.sent(id2)
  outbox.sent(id4)
  assert outbox.size() == 3
  assert db.outbox.count_documents({}) == 3
  item = next(outbox)
  assert item["msg"] == "msg 1"
  outbox.sent(item["id"])
  item = next(outbox)
  assert item["msg"] == "msg 3"
  outbox.sent(item["id"])
  item = next(outbox)
  assert item["msg"] == "msg 5"
  outbox.sent(item["id"])

def test_persistence():
  (original_db, outbox) = create_empty_outbox()
  id1 = outbox.add("topic", "msg 1")
  id2 = outbox.add("topic", "msg 2")
  id3 = outbox.add("topic", "msg 3")
  id4 = outbox.add("topic", "msg 4")
  id5 = outbox.add("topic", "msg 5")
  assert outbox.size() == 5
  (new_db, outbox) = create_empty_outbox()
  assert outbox.size() == 0
  (db, outbox) = create_empty_outbox(provided_db=original_db)
  assert outbox.size() == 5
  