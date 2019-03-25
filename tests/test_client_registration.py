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
    headers={"Authorization": _basic_auth_str("somebody","testing secret")},
    data=json.dumps(dict(foo="bar")),
    content_type="application/json"
  )
  assert response.status_code == 500 # error
  assert response.data == "invalid request: 'name'"

def test_correct_request(app, db):
  config.client.secret = "testing secret"
  request = {
    "name"  : "registration name",
    "pass"  : "registration pass",
    "pubkey": "registration pubky"
  }
  response = app.post(
    "/api/clients/register",  
    headers={"Authorization": _basic_auth_str("somebody","testing secret")},
    data=json.dumps(request),
    content_type="application/json"
  )
  assert response.status_code == 200 # ok

  assert db.list_collection_names() == [ "requests" ]
  assert [ x for x in db.requests.find({}, {"_id": False}) ] == [ request ]
