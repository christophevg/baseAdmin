import json

from requests.auth import _basic_auth_str

from baseadmin import config


def test_missing_authentication(app):
  response = app.post("/api/clients/register")
  assert response.status_code == 401 # unathorized

def test_incorrect_secret(app):
  config.client.secret = "testing secret"
  response = app.post(
    "/api/clients/register",  
    headers={"Authorization": _basic_auth_str("somebody","not testing secret")}
  )
  assert response.status_code == 401 # unathorized

def test_incorrect_request(app):
  config.client.secret = "testing secret"
  response = app.post(
    "/api/clients/register",  
    headers={"Authorization": _basic_auth_str("somebody", "testing secret")},
    data=json.dumps(dict(foo="bar")),
    content_type="application/json"
  )
  assert response.status_code == 500 # error
  assert response.data == b"failed to store registration request"

def test_correct_request(app, db):
  config.client.secret = "testing secret"
  request = {
    "pass"  : "registration pass",
    "pubkey": "registration pubkey"
  }
  response = app.post(
    "/api/clients/register",  
    headers={"Authorization": _basic_auth_str("somebody", "testing secret")},
    data=json.dumps(request),
    content_type="application/json"
  )
  assert response.status_code == 200 # ok

  assert db.list_collection_names() == [ "requests" ]
  assert db.requests.count_documents({}) == 1
  assert db.requests.find_one() == {
    "_id"   : "somebody",
    "pass"  : "registration pass",
    "pubkey": "registration pubkey"
  }
