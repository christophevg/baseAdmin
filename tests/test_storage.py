def test_provisioning(db):
  data = [ {"data" : 1 }, { "data" : 2 }, { "data" : 3 }]
  db.provision("test", data)
  assert db.list_collection_names() == [ "test" ]
  assert [ x for x in db.test.find() ] == data
