# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# Copyright (c) 2018 Reishin <hapy.lestat@gmail.com> and Contributors
import logging

from classes.async_tools import DNSProtocolClass
from dnslite.base import DNSPacket
from dnslite.constants import RCODE
from dnslite.datapack import in_addr_to_ip
from dnslite.types import QuestionItem, AnswerItem


class DNSHandlers(object):

  def __init__(self, myname, listen):
    self._myname = myname
    self._listen = listen

  def handle_a_record(self, q: QuestionItem) -> AnswerItem:
    if q.qname_str == self._myname:
      answer = q.get_answer(self._listen)
    else:
      ip = None
      # for docker in dockers:
      #   ip = docker.get_ip_info(q.qname_str)
      #   if ip:
      #     break

      if ip is None:
        return RCODE.NAME_ERROR

      answer = q.get_answer(ip)
    return answer

  def handle_ptr_record(self, q: QuestionItem) -> AnswerItem:
    if in_addr_to_ip(q.qname_str) == self._listen:
      answer = q.get_answer(self._myname)
    else:
      hostname = None
      # for docker in dockers:
      #   hostname = docker.container_name_by_ip(in_addr_to_ip(q.qname_str))
      #   if hostname:
      #     break

      if hostname is not None:
        answer = q.get_answer(hostname)
      else:
        answer = None

    return answer

  @staticmethod
  def handle_aaaa_record(q: QuestionItem) -> AnswerItem:
    return None

  def get_handlers(self):
    return {fn_name.split("_")[1].upper(): getattr(self, fn_name) for fn_name in dir(self) if fn_name.startswith("handle_")}


class DNSProtocol(DNSProtocolClass):
  def __init__(self):
    super(DNSProtocol, self).__init__()
    self.log = logging.getLogger(__name__)
    self.handlers = DNSHandlers(self._myname, self._listen).get_handlers()

  def datagram_received(self, data, addr):
    m = DNSPacket(data)

    for item in m.question_section:
      self.log.info(item)

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
