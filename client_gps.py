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


def main(port: int, status: bool):
  with serial.Serial('/dev/serial0', baudrate=9600, parity=PARITY_NONE, bytesize=EIGHTBITS, stopbits=STOPBITS_ONE) as ser:
    ser.readline() # trash first line

    #r = requests.get('https://sailingjackpot.ddns.net/nmea/gps?date=2022-06-01%2016:43:02&lat=N%2058%C2%B0%2026%27%2009.6%22&lon=E%20015%C2%B0%2037%27%2022.8%22')
    #print(r.status_code)

    gpx = gpxpy.gpx.GPX()

    # Create first track in our GPX:
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    # Create first segment in our GPX track:
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    count = 0
    index = 0

    while True:
      try:
        sentence = NMEA0183.bytes_to_sentence(ser.readline())
      except Exception:
        pass
      except KeyboardInterrupt:
        with open("output.gpx", "w") as f:
          f.write(gpx.to_xml())

        gpx_segment.simplify(100)
        with open("output_simplified.gpx", "w") as f:
          f.write(gpx.to_xml())
        sys.exit()
      else:
        if sentence.topic == b'RMC':
          count = count+1
          rmc = NMEA0183.RMC(sentence)
          #r = requests.get(f'https://sailingjackpot.ddns.net/nmea/gps?date={rmc.time}&lat={rmc.latitude}&lon={rmc.longitude}')
          #print(r.status_code)

          # Create points:
          gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(rmc.latitude, rmc.longitude, elevation=1234, time=rmc.time))
        if status:
          logging.info(sentence.topic)

        if count > 60*5:
          count = 0
          with open(f"output_{index}.gpx", "w") as f:
            f.write(gpx.to_xml())

          gpx_segment.simplify(100)
          with open(f"output_{index}_simplified.gpx", "w") as f:
            f.write(gpx.to_xml())
          index = index + 1

if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s [%(name)s] %(message)s')

  PARSER = argparse.ArgumentParser(description='NMEA0183 GPS client', allow_abbrev=False, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  PARSER.add_argument('--port', type=int, default=5556, help='port')
  PARSER.add_argument('--status', type=bool, default=False, help='Show status information')
  ARGS = PARSER.parse_args()

  main(ARGS.port, ARGS.status)
