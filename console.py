import logging
import time

import curses
import curses.textpad

import backend.client
from client import disable_console_logging

class Console(backend.client.base):
  def __init__(self, stdscr):
    super(self.__class__, self).__init__(name="console")
    disable_console_logging()
    self.stdscr = stdscr
    self.command = ""
    self.command_lines = 2;
    self.start()

  def start(self):
    super(self.__class__, self).start()
    self.setup_windows()
    self.follow("#")
    self.event_loop() 
    
  def setup_windows(self):
    curses.use_default_colors()
    self.stdscr.nodelay(1)
    self.log = curses.newwin(0, 0, 0, 0)
    self.log.scrollok(True)
    self.log.idlok(True)
    self.log.leaveok(True)
    self.bar = curses.newwin(0, 0, 0, 0)
    self.cli = curses.newwin(0, 0, 0, 0)
    self.prompt = curses.textpad.Textbox(self.cli, insert_mode=True)
    self.on_resize()

  def on_resize(self):
    self.detect_dimensions()
    self.log.resize(self.height-1-self.command_lines, self.width)
    self.log.refresh()
    self.bar.resize(1, self.width)
    self.bar.mvwin(self.height-1-self.command_lines, 0)
    self.bar.addstr(0, 0, "console" + " " * (self.width-7-1), curses.A_REVERSE)
    self.bar.refresh()
    self.cli.resize(self.command_lines, self.width)
    self.cli.mvwin(self.height-self.command_lines, 0)
    self.cli.refresh()

  def detect_dimensions(self):
    self.height, self.width = self.stdscr.getmaxyx()

  def event_loop(self):
    logging.info("starting console event loop, interrupt with Ctrl+c")
    try:
      while True:
        self.command = self.prompt.edit(self.validate_input)
        self.execute_command()
    except KeyboardInterrupt:
      pass

  def validate_input(self, ch):
    # remap backspace to "backspace" ;-)
    if ch == 127: return curses.KEY_BACKSPACE
    if ch == curses.KEY_RESIZE: self.on_resize()
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
