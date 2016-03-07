#!/usr/bin/python3

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# Copyright (c) 2015 Reishin <hapy.lestat@gmail.com> and Contributors

from dnslite.base import DNSPacket
from dnslite.constants import RCODE, QuestionTypes
from dnslite.datapack import ip_to_in_addr
from appcore.core import Configuration
from appcore.core import aLogger
from classes.docker import doker

from dnslite.types import QuestionItem, AnswerItem

import threading
import socket

conf = Configuration.get_instance()
log = aLogger.getLogger("main", conf)
listen = conf.get("listen", default="127.0.0.1", check_type=str)
port = conf.get("port", default=53, check_type=int)
listen_ptr = ip_to_in_addr(listen, 4)
myname = conf.get("myname", default="FakeServer", check_type=str)


def handle_a_record(q: QuestionItem) -> AnswerItem:
  if q.qname_str == myname:
    answer = q.get_answer(listen)
  else:
    ip = doker.get_ip_info(q.qname_str)
    if ip is None:
      return RCODE.NAME_ERROR

    answer = q.get_answer(ip)
  return answer


def handle_ptr_record(q: QuestionItem) -> AnswerItem:
  if q.qname_str == listen_ptr:
    answer = q.get_answer(myname)
  else:
    answer = None

  return answer


def handle_aaaa_record(q: QuestionItem) -> AnswerItem:
  return None


def handle_connection(sock):
  handlers = {
    "A": handle_a_record,
    "PTR": handle_ptr_record,
    "AAAA": handle_aaaa_record
  }

  while True:
    data, addr = sock.recvfrom(1024)
    m = DNSPacket(data)

    for item in m.question_section:
      log.debug(item)

    q = m.get_question(0)
    ret_code = RCODE.NO_ERROR

    if q.qtype_name in handlers:
      answer = handlers[q.qtype_name](q)
      if answer is None:
        pass  # send back empty answer section
      elif isinstance(answer, int):
        ret_code = answer
      else:
        m.add_answer(answer)
    else:
      ret_code = RCODE.NOT_IMPLEMENTED

    m.prepare_answer(ret_code)
    sock.sendto(m.raw(), addr)


def main():
  log.info("Start listening on udp %s:%s...", listen, port)
  udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  udps.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  udps.bind((listen, port))

  th = threading.Thread(target=handle_connection, args=(udps,))
  th.start()

  try:
    th.join()
  except KeyboardInterrupt:
    log.info("User interrupt, exiting....")
  finally:
    udps.close()

if __name__ == '__main__':
  main()
