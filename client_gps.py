#!/usr/bin/env python3

import argparse
import logging
import sys

import gpxpy
import gpxpy.gpx
import requests
import serial
from serial.serialutil import EIGHTBITS, PARITY_NONE, STOPBITS_ONE

import NMEA0183


class NMEA_GPS:
  def __init__(self, status):
    self._status = status
    self._alive = True

    self._time = None
    self._speed = None
    self._heading = None
    self._latitude = None
    self._longitude = None
    self._altitude = None

    self.gpx = None

  def new_file(self):
    if self.gpx:
      with open(self.filename, 'w') as f:
        f.write(self.gpx.to_xml())
        r = requests.get(f'https://sailingjackpot.ddns.net/nmea/gps?date={self._time}&lat={self._latitude}&lon={self._longitude}')
        if self._status:
          logging.info(f'request status: {r.status_code}')

    self.filename = f'{self._time}.gpx'
    if self._status:
      logging.info(f'New file started to record: {self.filename}')

    self.gpx = gpxpy.gpx.GPX()

    # Create first track in our GPX:
    self.gpx_track = gpxpy.gpx.GPXTrack()
    self.gpx.tracks.append(self.gpx_track)

    # Create first segment in our GPX track:
    self.gpx_segment = gpxpy.gpx.GPXTrackSegment()
    self.gpx_track.segments.append(self.gpx_segment)

  def update(self):
    if not self.gpx:
      self.new_file()

    self.gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(self._latitude, self._longitude, elevation=self._altitude, time=self._time))
    if len(self.gpx_segment.points) >= 60*15:
      self.new_file()

  def main(self):
    with serial.Serial('/dev/serial0', baudrate=9600, parity=PARITY_NONE, bytesize=EIGHTBITS, stopbits=STOPBITS_ONE) as ser:
      ser.readline() # trash first line
      while self._alive:
        try:
          sentence = NMEA0183.bytes_to_sentence(ser.readline())
          if self._status:
            logging.info(sentence)
        except Exception as e:
          if self._status:
            logging.error(e)
        except KeyboardInterrupt:
          self._alive = False
        else:
          if sentence.topic == b'RMC':
            rmc = NMEA0183.RMC(sentence)
            self._time = rmc.time
            self._speed = rmc.speed
            self._heading = rmc.heading
            self._latitude = rmc.latitude
            self._longitude = rmc.longitude
            self.update()

if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s [%(name)s] %(message)s')

  PARSER = argparse.ArgumentParser(description='NMEA0183 GPS client', allow_abbrev=False, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  PARSER.add_argument('--status', type=bool, default=False, help='Show status information')
  ARGS = PARSER.parse_args()

  gps_client = NMEA_GPS(ARGS.status)
  gps_client.main()
