#!/usr/bin/python3

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# Copyright (c) 2015 Reishin <hapy.lestat@gmail.com> and Contributors

from dnslite.base import DNSPacket
from dnslite.constants import RCODE, QuestionTypes
from dnslite.datapack import in_addr_to_ip
from apputils.core import Configuration
from classes.docker import DockerInfo
from dnslite.types import QuestionItem, AnswerItem

import logging
import socket

import asyncio


conf = Configuration()
dockers = [DockerInfo(url) for url in conf.get("docker")]

logging.basicConfig(level=logging.INFO, format='%(threadName)s %(message)s')

log = logging.getLogger(__name__)
listen = conf.get("listen", default="127.0.0.1", check_type=str)
port = conf.get("port", default=53, check_type=int)
myname = conf.get("myname", default="FakeServer", check_type=str)


def handle_a_record(q: QuestionItem) -> AnswerItem:
  if q.qname_str == myname:
    answer = q.get_answer(listen)
  else:
    ip = None
    for docker in dockers:
      ip = docker.get_ip_info(q.qname_str)
      if ip:
        break

    if ip is None:
      return RCODE.NAME_ERROR

    answer = q.get_answer(ip)
  return answer


def handle_ptr_record(q: QuestionItem) -> AnswerItem:
  if in_addr_to_ip(q.qname_str) == listen:
    answer = q.get_answer(myname)
  else:
    hostname = None
    for docker in dockers:
      hostname = docker.container_name_by_ip(in_addr_to_ip(q.qname_str))
      if hostname:
        break

    if hostname is not None:
      answer = q.get_answer(hostname)
    else:
      answer = None

  return answer


def handle_aaaa_record(q: QuestionItem) -> AnswerItem:
  return None


class DNSProtocol(asyncio.DatagramProtocol):
  sock = None
  handlers = {
    "A": handle_a_record,
    "PTR": handle_ptr_record,
    "AAAA": handle_aaaa_record
  }

  def datagram_received(self, data, addr):
    m = DNSPacket(data)

    for item in m.question_section:
      log.info(item)

    q = m.get_question(0)
    ret_code = RCODE.NO_ERROR

    if q.qtype_name in self.handlers:
      answer = self.handlers[q.qtype_name](q)
      if answer is None:
        pass  # send back empty answer section
      elif isinstance(answer, int):
        ret_code = answer
      else:
        m.add_answer(answer)
    else:
      ret_code = RCODE.NOT_IMPLEMENTED

    m.prepare_answer(ret_code)
    self.sock.sendto(m.raw(), addr)

  def error_received(self, exc):
    pass


def main():
  loop = asyncio.get_event_loop()

  log.info("Start listening on udp %s:%s...", listen, port)

  DNSProtocol.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  DNSProtocol.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  DNSProtocol.sock.bind((listen, port))

  _server = loop.create_datagram_endpoint(DNSProtocol, sock=DNSProtocol.sock)
  loop.run_until_complete(_server)
  loop.run_forever()


if __name__ == '__main__':
  main()
