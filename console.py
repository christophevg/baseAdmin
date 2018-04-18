import logging
import time

import curses
import curses.textpad

import local.config
import local.logging

import remote.client

class Console(remote.client.Base):
  def __init__(self, stdscr):
    super(self.__class__, self).__init__(name="console")
    self.stdscr = stdscr
    self.command = ""
    self.setup_windows()
    self.run()
    self.follow("#")
    self.event_loop() 
    
  def setup_windows(self):
    curses.use_default_colors()
    # curses.curs_set(0)
    self.stdscr.nodelay(1)
    self.detect_dimensions()
    self.log = curses.newwin(self.height-2, self.width, 0, 0)
    self.log.refresh()
    self.log.scrollok(True)
    self.log.idlok(True)
    self.log.leaveok(True)
    self.bar = curses.newwin(1, self.width, self.height-2, 0)
    self.bar.addstr(0, 0, "console" + " " * (self.width-7-1), curses.A_REVERSE)
    self.bar.refresh()
    self.cli = curses.newwin(1, self.width, self.height-1, 0)
    self.prompt = curses.textpad.Textbox(self.cli, insert_mode=True)

  def detect_dimensions(self):
    self.height, self.width = self.stdscr.getmaxyx()

  def event_loop(self):
    logging.info("starting console event loop, interrupt with Ctrl+c")
    try:
      while True:
        self.command = text = self.prompt.edit(self.validate_input)
        self.execute_command()
    except KeyboardInterrupt:
      pass

  def validate_input(self, ch):
    # remap backspace to "backspace" ;-)
    if ch == 127: return curses.KEY_BACKSPACE
    # TODO curses.RESIZE event
    # TODO add history
    return ch

  def execute_command(self):
    if len(self.command) < 1: return
    logging.debug("executing command: " + self.command)
    self.publish("console/command", self.command)
    self.command = ""
    self.cli.clear()

  def handle_mqtt_message(self, topic, msg):
    y, x = curses.getsyx()

    # TODO add timestamp?
    self.log.addstr(topic + ": " + msg+"\n")
    self.log.refresh()

    curses.setsyx(y, x)
    self.cli.refresh()

if __name__ == "__main__":
  curses.wrapper(Console)
