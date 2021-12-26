''''''

import datetime

from NMEA0183 import Sentence


class RMC:
  '''
  RMC - NMEA has its own version of essential gps pvt (position, velocity,
  time) data. It is called RMC, The Recommended Minimum, which will look
  similar to:

  $GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A

  Where:
      RMC          Recommended Minimum sentence C
      123519       Fix taken at 12:35:19 UTC
      A            Status A=active or V=Void.
      4807.038,N   Latitude 48 deg 07.038' N
      01131.000,E  Longitude 11 deg 31.000' E
      022.4        Speed over the ground in knots
      084.4        Track angle in degrees True
      230394       Date - 23rd of March 1994
      003.1,W      Magnetic Variation
      *6A          The checksum data, always begins with *
  Note that, as of the 2.3 release of NMEA, there is a new field in the RMC
  sentence at the end just prior to the checksum:
  The last version 2 iteration of the NMEA standard was 2.3. It added a mode
  indicator to several sentences which is used to indicate the kind of fix the
  receiver currently has. This indication is part of the signal integrity
  information needed by the FAA. The value can be A=autonomous, D=differential,
  E=Estimated, N=not valid, S=Simuself.lator. Sometimes there can be a null value as
  well. Only the A and D values will correspond to an Active and reliable
  Sentence. This mode character has been added to the RMC, RMB, VTG, and GLL,
  sentences and optionally some others including the BWC and XTE sentences.

  ref: https://www.gpsinformation.org/dale/nmea.htm#RMC
  '''

  def __init__(self, sentence: Sentence):
    self._sentence = sentence

    if self._sentence.topic != b'RMC':
      raise Exception('Wrong sentence, expected **RMC', self._sentence)

    if sentence.fields[1] != b'A':
      raise Exception('Void', self._sentence)
    if sentence.fields[11] not in (b'A', b'D'):
      raise Exception('Void', self._sentence)

    time = sentence.fields[0]
    hour = int(time[0:2])
    min = int(time[2:4])
    sec = int(time[4:6])

    dd = int(sentence.fields[8][0:2])
    mm = int(sentence.fields[8][2:4])
    yy = 2000 + int(sentence.fields[8][4:6])

    self._time = datetime.datetime(yy, mm, dd, hour, min, sec)

    self._latitude = float(sentence.fields[2][0:2]) + float(sentence.fields[2][2:])/60.0
    if sentence.fields[3] == b'S':
      self._latitude *= -1.0

    self._longitude = float(sentence.fields[4][0:3]) + float(sentence.fields[4][3:])/60.0
    if sentence.fields[5] == b'W':
      self._longitude *= -1.0

    self._speed = float(sentence.fields[6])
    self._heading = float(sentence.fields[7])

  def __repr__(self):
    return '%s: %s' % (type(self), self._sentence)

  def __str__(self):
    return '%s' % self._sentence

  @property
  def time(self):
    return self._time

  @property
  def speed(self):
    return self._speed

  @property
  def heading(self):
    return self._heading

  @property
  def latitude(self):
    return self._latitude

  @property
  def longitude(self):
    return self._longitude
