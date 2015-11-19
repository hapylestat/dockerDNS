from docker import Client
import socket
import time

from dnslite.base import DNSPacket
from dnslite.constants import RCODE
from dnslite.types import QuestionItem
from dnslite.datapack import ip_to_in_addr


ip_cache = {}


def recache(q: QuestionItem):
  global ip_cache
  try:
    info = c.inspect_container(q.qname[0])
    ip_cache[q.qname_str] = info["NetworkSettings"]["IPAddress"]
  except Exception as e:
    print(str(e))


if __name__ == '__main__':

  c = Client("tcp://1.1.1.1:4243")
  ip = '127.0.0.1'

  udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  myip = "127.0.0.3"
  myip_inaddr = ip_to_in_addr("127.0.0.3", 4)
  udps.bind((myip, 53))

  ip_cache[myip_inaddr] = "127.0.0.1"

  try:
    while 1:
      data, addr = udps.recvfrom(1024)
      m = DNSPacket(data)

      for item in m.question_section:
        print(item)

      q = m.get_question(0)

      RET_CODE = RCODE.NO_ERROR
      if q.qtype_name == "A" and q.qname_str != myip_inaddr:
        recache(q)
        if q.qname_str in ip_cache:
          ip = ip_cache[q.qname_str]
          m.add_answer(q.get_answer(ip))
        else:
          RET_CODE = RCODE.SERVER_FAILURE
      elif q.qtype_name == "PTR" and q.qname_str == myip_inaddr:
          m.add_answer(q.get_answer("fake.server"))
      else:
        RET_CODE = RCODE.NOT_IMPLEMENTED

      m.prepare_answer(RET_CODE)

      udps.sendto(m.raw(), addr)

      print('Response: %s. -> %s' % (".".join(m.get_question(0).qname), ip))
      time.sleep(0.02)
  except KeyboardInterrupt:
    print('Finalize')
    udps.close()
