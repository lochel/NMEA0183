''''''

import datetime

from NMEA0183 import Sentence


class GSV:
  '''
  GSV - Satellites in View shows data about the satellites that the unit might
  be able to find based on its viewing mask and almanac data. It also shows
  current ability to track this data. Note that one GSV sentence only can
  provide data for up to 4 satellites and thus there may need to be 3 sentences
  for the full information. It is reasonable for the GSV sentence to contain
  more satellites than GGA might indicate since GSV may include satellites that
  are not used as part of the solution. It is not a requirment that the GSV
  sentences all appear in sequence. To avoid overloading the data bandwidth some
  receivers may place the various sentences in totally different samples since
  each sentence identifies which one it is.

  The field called SNR (Signal to Noise Ratio) in the NMEA standard is often
  referred to as signal strength. SNR is an indirect but more useful value that
  raw signal strength. It can range from 0 to 99 and has units of dB according
  to the NMEA standard, but the various manufacturers send different ranges of
  numbers with different starting numbers so the values themselves cannot
  necessarily be used to evaluate different units. The range of working values
  in a given gps will usually show a difference of about 25 to 35 between the
  lowest and highest values, however 0 is a special case and may be shown on
  satellites that are in view but not being tracked.

  $GPGSV,2,1,08,01,40,083,46,02,17,308,41,12,07,344,39,14,22,228,45*75

  Where:
      GSV          Satellites in view
      2            Number of sentences for full data
      1            sentence 1 of 2
      08           Number of satellites in view

      01           Satellite PRN number
      40           Elevation, degrees
      083          Azimuth, degrees
      46           SNR - higher is better
          for up to 4 satellites per sentence
      *75          the checksum data, always begins with *

  ref: https://www.gpsinformation.org/dale/nmea.htm#GSV
  '''

  def __init__(self, sentence: Sentence):
    self._sentence = sentence

    data = self._sentence.msg.split(b',')
    if self._sentence.topic != b'GSV':
      raise Exception('Wrong sentence, expected **GSV', self._sentence)

    self._numberOfSentences = int(data[1])
    self._index = int(data[2])
    self._numberOfSatellites = int(data[3])

    self._satellites = list()
    i = 0
    while len(data) >= 4 + (i+1)*4:
      if data[4 + i*4]:
        self._satellites.append((data[4 + i*4 + 0], data[4 + i*4 + 1], data[4 + i*4 + 2], data[4 + i*4 + 3]))
      i += 1

  def __repr__(self):
    return '%s: %s' % (type(self), self._sentence)

  def __str__(self):
    return '%s' % self._sentence

  @property
  def numberOfSatellites(self):
    return self._numberOfSatellites

  @property
  def index(self):
    return self._index

  @property
  def numberOfSentences(self):
    return self._numberOfSentences

  @property
  def satellites(self):
    return self._satellites
