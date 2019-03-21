import mongomock

from baseadmin import storage
from baseadmin import pki

@mongomock.patch()
def test_provisioning():  
  pki.init()
  assert storage.db.list_collection_names() == [ "pki" ]
  assert len([x for x in storage.db.pki.find()]) == 1
  storage.db.pki.drop() # persistent across testing instances
