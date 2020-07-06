#!/usr/bin/env python3

import argparse
import logging

import serial
import zmq


def main(port: int, status: bool):
  context = zmq.Context()
  #pylint: disable=no-member
  socket = context.socket(zmq.PUB)
  socket.bind('tcp://*:%s' % port)

  with serial.Serial('/dev/serial0', 9600, timeout=5) as ser:
    ser.readline() # trash first line

    while True:
      message = ser.readline()
      socket.send(message)

      if status:
        print(message)

if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s [%(name)s] %(message)s')

  PARSER = argparse.ArgumentParser(description='This runs the NMEA0183 GPS client', allow_abbrev=False, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  PARSER.add_argument('--port', type=int, default=5556, help='port')
  PARSER.add_argument('--status', type=bool, default=False, help='Show status information')
  ARGS = PARSER.parse_args()

  main(ARGS.port, ARGS.status)
