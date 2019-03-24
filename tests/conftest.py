import pytest

import mongomock

from baseadmin import config
from baseadmin.storage import db as store

from baseadmin.backend.web import server


@pytest.fixture
def db():
  config.store.uri = "mongodb://localhost:27017/testing"
  store.mongo      = mongomock.MongoClient()
  store.instance   = None
  return store

@pytest.fixture
def app():
  return server.test_client()
