''''''

class Sentence:
  def __init__(self, raw: bytes):
    self._raw = raw

    if self._raw[0] != ord('$'):
      raise Exception('Invalid prefix', self._raw)
    if self._raw[-2:] != b'\r\n':
      raise Exception('Invalid suffix', self._raw)

    if self._raw[-5] == ord('*'):
      self._msg = self._raw[1:-5]
      self._checksum = self._raw[-4:-2]

      if int(self.checksum, 16) != self._calculate_checksum():
        raise Exception('Wrong checksum', self._raw)
    else:
      self._msg = self._raw[1:-2]
      self._checksum = None

    self._talker = self._raw[1:3]
    self._topic = self._raw[3:6]

  def __repr__(self):
    return '%s: %s' % (type(self), self._raw[:-2].decode())

  def __str__(self):
    return self._raw[:-2].decode()

  @property
  def raw(self):
    return self._raw

  @property
  def talker(self):
    return self._talker

  @property
  def topic(self):
    return self._topic

  @property
  def msg(self):
    return self._msg

  @property
  def checksum(self):
    return self._checksum

  def _calculate_checksum(self):
    sum = 0
    for c in self._msg:
      sum = sum ^ c # xor
    return sum
