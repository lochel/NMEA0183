#!/usr/bin/env python3

import argparse
import logging

import serial
import zmq
from serial.serialutil import EIGHTBITS, PARITY_NONE, STOPBITS_ONE


def main(port: int, status: bool):
  context = zmq.Context()
  #pylint: disable=no-member
  socket = context.socket(zmq.PUB)
  socket.bind('tcp://*:%s' % port)

  with serial.Serial('/dev/serial0', baudrate=4800, parity=PARITY_NONE, bytesize=EIGHTBITS, stopbits=STOPBITS_ONE) as ser:
    ser.readline() # trash first line

    while True:
      sentence = ser.readline()
      socket.send(sentence)

      if status:
        logging.info(sentence[:-2].decode('utf-8'))

if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s [%(name)s] %(message)s')

  PARSER = argparse.ArgumentParser(description='NMEA0183 GPS client', allow_abbrev=False, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  PARSER.add_argument('--port', type=int, default=5556, help='port')
  PARSER.add_argument('--status', type=bool, default=False, help='Show status information')
  ARGS = PARSER.parse_args()

  main(ARGS.port, ARGS.status)
