from baseadmin.storage import db
from baseadmin.pki     import keys

from mqfactory                      import Threaded, MessageQueue
from mqfactory.transport.mqtt       import MQTTTransport
from mqfactory.transport.qos        import Acknowledging
from mqfactory.message.format.js    import JsonFormatting
from mqfactory.store                import Persisting
from mqfactory.store.mongo          import MongoCollection
from mqfactory.message.security     import Signing
from mqfactory.message.security.rsa import RsaSignature

mq = JsonFormatting(
       Signing(
         Acknowledging(
           Persisting(
             Threaded(
               MessageQueue(
                 MQTTTransport("mqtt://localhost:1883")
               )
             ),
             inbox=MongoCollection(db.inbox),
             outbox=MongoCollection(db.outbox)
           )
         ),
         adding=RsaSignature(keys, me="")
       )
     )
