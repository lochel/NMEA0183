''''''

from NMEA0183 import Sentence


class GSA:
  '''
  GSA - GPS DOP and active satellites. This sentence provides details on the
  nature of the fix. It includes the numbers of the satellites being used in
  the current solution and the DOP. DOP (dilution of precision) is an indication
  of the effect of satellite geometry on the accuracy of the fix. It is a
  unitless number where smaller is better. For 3D fixes using 4 satellites a 1.0
  would be considered to be a perfect number, however for overdetermined
  solutions it is possible to see numbers below 1.0.

  There are differences in the way the PRN's are presented which can effect the
  ability of some programs to display this data. For example, in the example
  shown below there are 5 satellites in the solution and the null fields are
  scattered indicating that the almanac would show satellites in the null
  positions that are not being used as part of this solution. Other receivers
  might output all of the satellites used at the beginning of the sentence with
  the null field all stacked up at the end. This difference accounts for some
  satellite display programs not always being able to display the satellites
  being tracked. Some units may show all satellites that have ephemeris data
  without regard to their use as part of the solution but this is non-standard.

  $GPGSA,A,3,04,05,,09,12,,,24,,,,,2.5,1.3,2.1*39

  Where:
      GSA      Satellite status
      A        Auto selection of 2D or 3D fix (M = manual)
      3        3D fix - values include: 1 = no fix
                                        2 = 2D fix
                                        3 = 3D fix
      04,05... PRNs of satellites used for fix (space for 12)
      2.5      P-DOP (dilution of precision)
      1.3      Horizontal dilution of precision (H-DOP)
      2.1      Vertical dilution of precision (V-DOP)
      *39      the checksum data, always begins with *

  ref: https://www.gpsinformation.org/dale/nmea.htm#GSA
  '''

  def __init__(self, sentence: Sentence):
    self._sentence = sentence

    if self._sentence.topic != b'GSA':
      raise Exception('Wrong sentence, expected **GSA', self._sentence)

    self._dop = float(sentence.fields[14])
    self._hdop = float(sentence.fields[15])
    self._vdop = float(sentence.fields[16])

  def __repr__(self):
    return '%s: %s' % (type(self), self._sentence)

  def __str__(self):
    return '%s' % self._sentence

  @property
  def dop(self) -> float:
    '''P-DOP (dilution of precision)'''
    return self._dop

  @property
  def hdop(self) -> float:
    '''Horizontal dilution of precision (H-DOP)'''
    return self._hdop

  @property
  def vdop(self) -> float:
    '''Vertical dilution of precision (V-DOP)'''
    return self._vdop
