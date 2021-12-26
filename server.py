#!/usr/bin/env python3
''''''

import argparse
import logging

import zmq

import NMEA0183


class Server:
  def __init__(self):
    self._logger = logging.getLogger(__name__)
    self._context = zmq.Context()
    #pylint: disable=no-member
    self._socket = self._context.socket(zmq.SUB)
    self._socket.setsockopt(zmq.SUBSCRIBE, b'')

    self._talkers = set()
    self._unsupported = set()
    self._supported = {
      b'RMC': self.RMC,
      b'GSA': self.GSA,
      b'VTG': self.VTG,
      b'GGA': self.GGA,
      b'GSV': self.GSV}

    self._satellites = list()
    self._satellites_tmp = list()

    self._time = None

  def connect(self, addr: str):
    self._socket.connect(addr)
    print('Collecting updates from %s...' % addr)

  def subscribe(self, topic: str):
    topic = '$' + topic
    self._socket.setsockopt(zmq.UNSUBSCRIBE, b'')
    self._socket.setsockopt(zmq.SUBSCRIBE, topic.encode('ascii'))
    print('Subscribing to "{}"'.format(topic))

  def run(self):
    while True:
      raw = self._socket.recv()
      sen = NMEA0183.bytes_to_sentence(raw)

      if sen.talker not in self._talkers:
        self._talkers.add(sen.talker)
        self._logger.info('New talker: %s', sen.talker)
        print(self._talkers)

      if sen.topic in self._supported:
        self._supported[sen.topic](sen)
      elif sen.topic not in self._unsupported:
        self._unsupported.add(sen.topic)
        self._logger.warning('Unsupported topic: %s', sen.topic.decode())

  def RMC(self, sen: NMEA0183.Sentence):
    rmc = NMEA0183.RMC(sen)
    self._time = rmc.time
    print('RMC: Time %s, Lon %s, Lat %s, Speed %s, Heading %s' % (rmc.time, rmc.longitude, rmc.latitude, rmc.speed, rmc.heading))

  def GSA(self, sen: NMEA0183.Sentence):
    gsa = NMEA0183.GSA(sen)
    #print(gsa)
    print('GSA: dop %s, hdop %s, vdop %s' % (gsa.dop, gsa.hdop, gsa.vdop))

  def VTG(self, sen: NMEA0183.Sentence):
    #print(sen)
    pass

  def GGA(self, sen: NMEA0183.Sentence):
    #print(sen)
    pass

  def GSV(self, sen: NMEA0183.Sentence):
    gsv = NMEA0183.GSV(sen)

    if gsv.index == 1:
      self._satellites_tmp = list()

    self._satellites_tmp.extend(gsv._satellites)

    if gsv.index == gsv.numberOfSentences:
      self._satellites = self._satellites_tmp
      print('GSV: %d %s' % (gsv.numberOfSatellites, self._satellites))
      #NMEA0183.plot_gsv(self._satellites, self._time)

def _main():
  logging.basicConfig(level=logging.INFO, format='%(levelname)s [%(name)s] %(message)s')

  parser = argparse.ArgumentParser(description='NMEA0183 server', allow_abbrev=False, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('--connect', type=str, action='append', required=True)
  parser.add_argument('--topic', type=str, action='append')
  args = parser.parse_args()

  server = Server()
  for addr in args.connect:
    server.connect(addr)
  if args.topic:
    for topic in args.topic:
      server.subscribe(topic)
  server.run()

if __name__ == '__main__':
  _main()
