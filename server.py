#!/usr/bin/env python3
''''''

import argparse
import datetime
import logging
import sys

import zmq

import NMEA0183


class Server:
  def __init__(self):
    self._context = zmq.Context()
    #pylint: disable=no-member
    self._socket = self._context.socket(zmq.SUB)
    self._socket.setsockopt(zmq.SUBSCRIBE, b'')

  def connect(self, addr: str):
    self._socket.connect(addr)
    print('Collecting updates from %s...' % addr)

  def run(self):
    while True:
      msg = self._socket.recv()
      print(NMEA0183.Sentence(msg))

if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s [%(name)s] %(message)s')

  PARSER = argparse.ArgumentParser(description='This runs the NMEA0183 server', allow_abbrev=False, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  PARSER.add_argument('--connect', type=str, action='append')
  ARGS = PARSER.parse_args()

  SERVER = Server()
  for addr in ARGS.connect:
    SERVER.connect(addr)
  SERVER.run()
