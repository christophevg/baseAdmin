import os
import psutil
import datetime
import time
import calendar
import subprocess
import logging
import json

import client.service
from client.service import API

@API.endpoint(port=18181)
class ReportingService(client.service.base):

  def uptime(self):
    now = datetime.datetime.now()
    current_timestamp = time.mktime(now.timetuple())
    return current_timestamp - psutil.boot_time()

  def temperature(self):
    try:
      temperature = subprocess.check_output(
        ["/opt/vc/bin/vcgencmd", "measure_temp"]
      ).strip()
      return float(temperature[5:-2])
    except:
      return 0

  def collect(self):
    return {
      "load":           os.getloadavg(),
      "idle":           psutil.cpu_times_percent(interval=1, percpu=False)[3],
      "cpu_percent":    psutil.cpu_percent(interval=3),
      "virtual_memory": psutil.virtual_memory(),
      "disk_usage":     psutil.disk_usage('/'),
      "uptime":         self.uptime(),
      "temperature":    self.temperature(),
      "system_time":    calendar.timegm(datetime.datetime.utcnow().timetuple())
    }

  def reporting_interval(self):
    try:
      return self.config["interval"]
    except:
      return 60

  def loop(self):
    if self.config != None:
      start = time.time()
      self.publish("stats", self.collect())
      delay = time.time() - start
      time.sleep(self.reporting_interval()-delay)
    else:
      time.sleep(.300)

if __name__ == "__main__":
  ReportingService().run()
