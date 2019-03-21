import mongomock

from baseadmin import storage

@mongomock.patch()
def test_provisioning():
  storage.init()
  data = [ {"data" : 1 }, { "data" : 2 }, { "data" : 3 }]
  storage.provision("test", data)
  assert storage.db.list_collection_names() == [ "test" ]
  assert [ x for x in storage.db.test.find() ] == data
  storage.db.test.pki.drop() # persistent across testing instances
