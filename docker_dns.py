from docker import Client
import socket
import time

# Book - http://www.zytrax.com/books/dns/ch15/


class DNSQuery:
  def __init__(self, data):
    self.data = data
    self.dominio = ''

    tipo = (data[2] >> 3) & 15   # Opcode bits
    if tipo == 0:                # Standard query
      ini = 12
      lon = data[ini]
      while lon != 0:
        self.dominio += data[ini + 1:ini + lon + 1].decode() + '.'
        ini += lon + 1
        lon = data[ini]

  def response(self, ip):
    byte_ip = bytearray(map(lambda x: int(x), ip.split('.')))

    packet = b''
    if self.dominio:
      packet += self.data[:2] + b"\x81\x80"
      packet += self.data[4:6] + self.data[4:6] + b'\x00\x00\x00\x00'     # Questions and Answers Counts
      packet += self.data[12:]                                           # Original Domain Name Question
      packet += b'\xc0\x0c'                                               # Pointer to domain name
      packet += b'\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'               # Response type, ttl and resource data length -> 4 bytes
      packet += byte_ip  # 4bytes of IP
    return packet

ipsettings = {}


def recache(name):
  global ipsettings
  try:
    info = c.inspect_container(name)
    ipsettings[name] = info["NetworkSettings"]["IPAddress"]
  except Exception as e:
    print(str(e))


def bitfield(n):
  return [int(digit) for digit in bin(n)[2:]] # [2:] to chop off the "0b" part

class InputMessage(object):
  _four_bytes = 0b0000000000001111
  _one_byte = 0b0000000000000001
  _base = 16
  _flags = {
    "qr": [1, _one_byte],
    "opcode": [2, _four_bytes],
    "aa": [6, _one_byte],
    "tc": [7, _one_byte],
    "rd": [8, _one_byte],
    "ra": [9, _one_byte],
    "res1": [10, _one_byte],
    "res2": [11, _one_byte],
    "res3": [12, _one_byte],
    "rcode": [13, _four_bytes]
  }

  def _get_bit(self, _bitfield, name):
    _bit_pos = self._base - self._flags[name][0]
    _bit_mask = self._flags[name][1]
    return (_bitfield >> _bit_pos) & _bit_mask

  def __init__(self, _msg):
    """
    :type _msg byte
    :param _msg Get byte array as input and form structured data
    """
    self.message_id = _msg[:2]
    _pack1 = int.from_bytes(_msg[2:4], byteorder="big")
    _qdcount = int.from_bytes(_msg[4:6], byteorder="big")
    _ancount = int.from_bytes(_msg[6:8], byteorder="big")
    _nscount = int.from_bytes(_msg[8:10], byteorder="big")
    _arcount = int.from_bytes(_msg[10:12], byteorder="big")

    #  decode header section
    self.qr = self._get_bit(_pack1, "qr")
    self.opcode = self._get_bit(_pack1, "opcode")
    self.aa = self._get_bit(_pack1, "aa")
    self.tc = self._get_bit(_pack1, "tc")
    self.rd = self._get_bit(_pack1, "rd")
    self.ra = self._get_bit(_pack1, "ra")
    self.res1 = self._get_bit(_pack1, "res1")
    self.res2 = self._get_bit(_pack1, "res2")
    self.res3 = self._get_bit(_pack1, "res3")
    self.rcode = self._get_bit(_pack1, "rcode")

    # decode Question section

    # decode Answer section

    # decode Authority section

    # decode Additional section



  def __str__(self):
    out = ""
    for field in self.__dir__():
      if field[:1] != "_" and field[:2] != "__" and not hasattr(self.__getattribute__(field), "__call__"):
        out += "%s: %s\n" % (field, self.__getattribute__(field))
    return out



if __name__ == '__main__':
  msg = b'9\xc5\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x05node2\x04test\x02me\x00\x00\x01\x00\x01'
  msg = InputMessage(msg)
  print(msg)
  exit(0)


  c = Client("tcp://1.1.1.1:4243")
  ip = '127.0.0.1'

  udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  udps.bind(('127.0.0.3', 53))

  try:
    while 1:
      data, addr = udps.recvfrom(1024)
      m = InputMessage(data)
      print(m)

      p = DNSQuery(data)
      domain = p.dominio[:-1]
      domain = domain.split(".")[0]
      recache(domain)

      if domain in ipsettings:
        ip = ipsettings[domain]

      udps.sendto(p.response(ip), addr)

      print('Response: %s -> %s' % (p.dominio, ip))
      time.sleep(0.02)
  except KeyboardInterrupt:
    print('Finalize')
    udps.close()
