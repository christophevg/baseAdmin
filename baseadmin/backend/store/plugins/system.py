from backend.store.plugins import Monitor

class SystemMonitor(Monitor):
  def follows(self):
    return [ "client/+/service/ReportingService/stats" ]

  def handle(self, topic, stats):
    if len(topic) != 5: return
    client = topic[1]

    self.store.system.update_one(
      { "_id": client },
      { "$push"  : { "stats" : {
        "$each"  : [ stats ],
        "$sort"  : { "system_time" : 1 },
        "$slice" : -12
      }}},
      upsert=True
    )
