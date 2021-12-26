#!/usr/bin/env python3

import argparse
import logging
import time

import zmq

import NMEA0183


def main(port: int, status: bool):
  context = zmq.Context()
  #pylint: disable=no-member
  socket = context.socket(zmq.PUB)
  socket.bind('tcp://*:%s' % port)

  while True:
    sentence = NMEA0183.Sentence('II', 'XDR', ['C','19.52','C','TempAir'], None)
    socket.send(sentence)

    if status:
      logging.info(sentence[:-2].decode('utf-8'))

    time.sleep(60)

if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s [%(name)s] %(message)s')

  PARSER = argparse.ArgumentParser(description='NMEA0183 temp client', allow_abbrev=False, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  PARSER.add_argument('--port', type=int, default=5557, help='port')
  PARSER.add_argument('--status', type=bool, default=False, help='Show status information')
  ARGS = PARSER.parse_args()

  main(ARGS.port, ARGS.status)
