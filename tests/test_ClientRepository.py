import mongomock

from baseadmin import init, get_db
init(mongomock.MongoClient().db)

from baseadmin.backend.repositories import clients

def test_registration_of_valid_request():
  db = get_db()
  request = {
    "name"      : "test name",
    "pass"      : "test pass",
    "pubkey"    : "test pubkey",
  }
  clients.register(request)

  assert db.requests.count_documents({}) == 1

  doc = db.requests.find_one()
  assert doc["name"]      == "test name"
  assert doc["pass"]      == "test pass"
  assert doc["pubkey"]    == "test pubkey"
