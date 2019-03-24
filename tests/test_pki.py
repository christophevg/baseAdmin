from baseadmin import pki

def test_provisioning(db):
  assert db.list_collection_names() == []
  pki.keys.provision()
  assert db.list_collection_names() == [ "pki" ]
  assert len([x for x in db.pki.find()]) == 1
