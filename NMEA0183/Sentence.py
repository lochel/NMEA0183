'''NMEA0183 Sentence'''

from typing import Union, Optional

def _to_bytes(raw: Union[str,bytes]) -> bytes:
  if isinstance(raw, str):
    return raw.encode('ascii')
  elif isinstance(raw, bytes):
    return raw
  raise Exception('Wrong type', raw)

class Sentence:
  def __init__(self, talker: Union[str,bytes], topic: Union[str,bytes], fields: list[Union[str,bytes]], checksum = Optional[Union[str,bytes]]):
    self._talker = _to_bytes(talker)
    self._topic = _to_bytes(topic)
    self._fields = [_to_bytes(field) for field in fields]
    self._checksum = _to_bytes(checksum) if checksum else None

  def __repr__(self) -> str:
    return '%s: %s' % (type(self), str(self))

  def __str__(self) -> str:
    return self.raw[0:-2].decode('utf-8')

  @property
  def raw(self):
    if self.checksum:
      return b'$' + self.msg + b'*' + self._checksum + b'\r\n'
    else:
      return b'$' + self.msg + b'\r\n'

  @property
  def talker(self):
    return self._talker

  @property
  def topic(self):
    return self._topic

  @property
  def msg(self):
    return b','.join([self._talker + self._topic] + self._fields)

  @property
  def fields(self):
    return self._fields

  @property
  def checksum(self):
    return self._checksum

def bytes_to_sentence(raw: bytes) -> Sentence:
  if raw[0] != ord('$'):
    raise Exception('Invalid prefix', raw)
  if raw[-2:] != b'\r\n':
    raise Exception('Invalid suffix', raw)

  talker = raw[1:3]
  topic = raw[3:6]

  if raw[-5] == ord('*'): # optional checksum
    msg = raw[1:-5]
    checksum = raw[-4:-2]

    if int(checksum, 16) != calculate_checksum(msg):
      raise Exception('Wrong checksum', raw)
  else:
    msg = raw[1:-2]
    checksum = None

  fields = msg.split(b',')[1:]
  return Sentence(talker, topic, fields, checksum)

def calculate_checksum(msg: bytes) -> int:
  sum = 0
  for c in msg:
    sum = sum ^ c # xor
  return sum
