from docker import Client
import socket
import time

from dnslite.base import DNSPacket
from dnslite.constants import RCODE
from dnslite.types import QuestionItem
from dnslite.datapack import ip_to_in_addr




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


def recache(q: QuestionItem):
  global ipsettings
  try:
    info = c.inspect_container(q.qname[0])
    ipsettings[q.qname_str] = info["NetworkSettings"]["IPAddress"]
  except Exception as e:
    print(str(e))


if __name__ == '__main__':

  c = Client("tcp://1.1.1.1:4243")
  ip = '127.0.0.1'

  udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  myip = "127.0.0.3"
  myip_inaddr = ip_to_in_addr("127.0.0.3", 4)
  udps.bind((myip, 53))

  ipsettings[myip_inaddr] = "127.0.0.1"

  try:
    while 1:
      data, addr = udps.recvfrom(1024)
      m = DNSPacket(data)

      for item in m.question_section:
        print(item)

      p = DNSQuery(data)
      q = m.get_question(0)

      if q.qtype_name == "A" and q.qname_str != myip_inaddr:
        recache(q)
        if q.qname_str in ipsettings:
          ip = ipsettings[q.qname_str]
          m.add_answer(q.get_answer(ip))
        m.prepare_answer()
      elif q.qtype_name == "PTR" and q.qname_str == myip_inaddr:
        m.add_answer(q.get_answer("fake.server"))
        m.prepare_answer()
      else:
        m.prepare_answer(RCODE.NOT_IMPLEMENTED)

      udps.sendto(m.raw(), addr)

      print('Response: %s. -> %s' % (".".join(m.get_question(0).qname), ip))
      time.sleep(0.02)
  except KeyboardInterrupt:
    print('Finalize')
    udps.close()
