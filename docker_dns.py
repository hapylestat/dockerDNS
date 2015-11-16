from docker import Client
import socket
import time

from dnslite.base import InputMessage

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


if __name__ == '__main__':
  # msg = b'9\xc5\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x05node2\x04test\x02me\x00\x00\x01\x00\x01'
  # msg = InputMessage(msg)
  # print(msg)
  # exit(0)


  c = Client("tcp://1.1.1.1:4243")
  ip = '127.0.0.1'

  udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  udps.bind(('127.0.0.3', 53))

  try:
    while 1:
      data, addr = udps.recvfrom(1024)
      m = InputMessage(data)

      for item in m.question_section:
        print(item)

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
