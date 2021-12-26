'''NMEA0183 Sentence'''

from typing import Union, Optional

def _to_bytes(raw: Union[str,bytes]) -> bytes:
  if isinstance(raw, str):
    return raw.encode('ascii')
  elif isinstance(raw, bytes):
    return raw
  raise Exception('Wrong type', raw)

class Sentence:
  def __init__(self, talker: Union[str,bytes], topic: Union[str,bytes], fields: list[Union[str,bytes]], checksum: Optional[Union[str,bytes]] = None):
    self._talker = _to_bytes(talker)
    self._topic = _to_bytes(topic)
    self._fields = [_to_bytes(field) for field in fields]
    self._checksum = calculate_checksum(self.msg)

    if checksum and _to_bytes(checksum) != self._checksum:
      raise Exception('Wrong checksum - got {} expected {}'.format(checksum, self._checksum), self)

  def __repr__(self) -> str:
    return '%s: %s' % (type(self), str(self))

  def __str__(self) -> str:
    return self.raw[0:-2].decode('utf-8')

  @property
  def raw(self) -> bytes:
    return b'$' + self.msg + b'*' + self._checksum + b'\r\n'

  @property
  def talker(self) -> bytes:
    return self._talker

  @property
  def topic(self) -> bytes:
    return self._topic

  @property
  def msg(self) -> bytes:
    return b','.join([self._talker + self._topic] + self._fields)

  @property
  def fields(self) -> list[bytes]:
    return self._fields

  @property
  def checksum(self) -> bytes:
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
  else:
    msg = raw[1:-2]
    checksum = None

  fields = msg.split(b',')[1:]
  return Sentence(talker, topic, fields, checksum)

def calculate_checksum(msg: bytes) -> bytes:
  # calculate checksum
  sum = 0
  for c in msg:
    sum = sum ^ c # xor

  # convert to two digits in hexadecimal
  if sum == 0:
    return b'00'

  alphabet = b'0123456789ABCDEF'
  digits = []
  while sum:
    digits.append(int(sum % 16))
    sum //= 16
  return bytes([alphabet[d] for d in digits[::-1]]).rjust(2, b'0')
