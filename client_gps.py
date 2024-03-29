#!/usr/bin/env python3

import argparse
import logging
import os
import shutil
import sys
import traceback
from logging.handlers import RotatingFileHandler

import gpxpy
import gpxpy.gpx
import requests
import serial
from serial.serialutil import EIGHTBITS, PARITY_NONE, STOPBITS_ONE

import NMEA0183


def configure(stdout: bool = True, rotating = False, loglevel: str = 'INFO') -> None:
  '''configure logging'''

  dir = 'log'
  filename = 'client_gps.log'

  if not os.path.isdir(dir):
    try:
      os.makedirs(dir)
    except OSError:
      raise Exception(f'Creation of the log directory "{dir}" failed')

  if not filename.endswith('.log'):
    filename += '.log'

  log_exists = os.path.isfile(os.path.join(dir, filename))
  format = '%(asctime)s: %(levelname)s [%(name)s] %(message)s'
  formatter = logging.Formatter(format)

  if rotating:
    handler = RotatingFileHandler(filename=os.path.join(dir, filename), mode='a', maxBytes=5*1024*1024, backupCount=2)
    handler.setFormatter(formatter)
    if log_exists:
      handler.doRollover()
    logging.getLogger().addHandler(handler)
  else:
    logging.basicConfig(filename=os.path.join(dir, filename), level=logging.INFO, format=format)

  if stdout:
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)

  # set log level
  numeric_level = getattr(logging, loglevel.upper(), None)
  if not isinstance(numeric_level, int):
    raise Exception(loglevel, 'invalid log level')
  logging.getLogger().setLevel(numeric_level)

  # always log version and command line arguments
  logging.getLogger().info(f'arguments: {sys.argv[1:]}')

class NMEA_GPS:
  def __init__(self):
    self._alive = True

    self._time = None
    self._speed = None
    self._heading = None
    self._latitude = None
    self._longitude = None
    self._altitude = None

    self.gpx = None

    if not os.path.exists('pending'):
      os.makedirs('pending')

    if not os.path.exists('uploaded'):
      os.makedirs('uploaded')

  def upload_position(self):
    try:
      r = requests.get(f'https://sailingjackpot.ddns.net/nmea/gps?date={self._time}&lat={self._latitude}&lon={self._longitude}&sog={self._speed}&cog={self._heading}')
      logging.info(f'{r.status_code}: {r.url}')
    except Exception:
      logging.info(f'Something went wrong; we\'ll try later again')
      logging.error(traceback.format_exc())

  def upload(self):
    self.upload_position()

    files = sorted([os.path.join('pending', f) for f in os.listdir('pending') if os.path.isfile(os.path.join('pending', f))])

    try:
      for file in files:
        with open(file) as f:
          data = f.read()

        r = requests.post('https://sailingjackpot.ddns.net/nmea/gpx', data=data, headers={'Content-Type': 'application/xml'})
        logging.info(f'{r.status_code}: {file}')

        if r.status_code == 200:
          #os.remove(file)
          shutil.move(file, 'uploaded')
    except Exception:
      logging.info(f'Something went wrong; we\'ll try later again')
      logging.error(traceback.format_exc())

  def new_file(self):
    if self.gpx:
      data = self.gpx.to_xml()
      with open(os.path.join('pending', self.filename), 'w') as f:
        f.write(data)

    self.filename = f'{self._time}.gpx'

    self.gpx = gpxpy.gpx.GPX()

    # Create first track in our GPX:
    self.gpx_track = gpxpy.gpx.GPXTrack()
    self.gpx.tracks.append(self.gpx_track)

    # Create first segment in our GPX track:
    self.gpx_segment = gpxpy.gpx.GPXTrackSegment()
    self.gpx_track.segments.append(self.gpx_segment)

  def update(self):
    if not self._altitude:
      return

    if not self.gpx:
      self.new_file()
      self.upload()

    self.gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(self._latitude, self._longitude, elevation=self._altitude, time=self._time))
    if len(self.gpx_segment.points) >= 60*10:
      self.new_file()
      self.upload()

  def main(self):
    with serial.Serial('/dev/serial0', baudrate=9600, parity=PARITY_NONE, bytesize=EIGHTBITS, stopbits=STOPBITS_ONE) as ser:
      ser.readline() # trash first line
      while self._alive:
        try:
          sentence = NMEA0183.bytes_to_sentence(ser.readline())
        except Exception as e:
          logging.error(e)
          logging.error(traceback.format_exc())
        except KeyboardInterrupt:
          self._alive = False
          print('\r', end='')
          logging.warning('shutdown due to keyboard interrupt')
        else:
          if sentence.topic == b'RMC':
            try:
              rmc = NMEA0183.RMC(sentence)
            except Exception:
              logging.error(traceback.format_exc())
            else:
              self._time = rmc.time
              self._speed = rmc.speed
              self._heading = rmc.heading
              self._latitude = rmc.latitude
              self._longitude = rmc.longitude
              self.update()
          elif sentence.topic == b'GGA':
            try:
              gga = NMEA0183.GGA(sentence)
            except Exception:
              logging.error(traceback.format_exc())
            else:
              self._altitude = gga.altitude

if __name__ == '__main__':
  PARSER = argparse.ArgumentParser(description='NMEA0183 GPS client', allow_abbrev=False, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  PARSER.add_argument('--stdout', action='store_true', help='enables logging to stdout')
  ARGS = PARSER.parse_args()

  configure(ARGS.stdout, rotating=True)

  gps_client = NMEA_GPS()
  try:
    gps_client.main()
  except:
    logging.error(traceback.format_exc())
    raise
  logging.warning('stop')
