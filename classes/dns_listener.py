# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# Copyright (c) 2018 Reishin <hapy.lestat@gmail.com> and Contributors
import logging

from classes.async_tools import DNSProtocolClass
from classes.storage import ContainerKeyStorage
from dnslite.base import DNSPacket
from dnslite.constants import RCODE, QuestionTypes
from dnslite.datapack import in_addr_to_ip
from dnslite.types import QuestionItem, AnswerItem


class DNSHandlers(object):

  def __init__(self, myname, listen):
    self._myname = myname
    self._listen = listen

  def handle_a_record(self, q: QuestionItem) -> AnswerItem:
    if q.qname_str == self._myname:
      return q.get_answer(self._listen)
    else:
      name = q.qname_str.partition(".")[0]  # we not really need a domain name
      container = ContainerKeyStorage.get_by_name(name)

      if container is None:
        return RCODE.NAME_ERROR

      return q.get_answer(container.ip)

  def handle_ptr_record(self, q: QuestionItem) -> AnswerItem or None:
    if in_addr_to_ip(q.qname_str) == self._listen:
      return q.get_answer(self._myname)
    else:
      container = ContainerKeyStorage.get_by_ip(in_addr_to_ip(q.qname_str))

      if not container:
        return None

      return q.get_answer(container.name)

  @staticmethod
  def handle_aaaa_record(q: QuestionItem) -> AnswerItem:
    return None

  @staticmethod
  def handle_txt_record(q: QuestionItem) -> AnswerItem:
    return q.get_answer("check later, not implemented yet")

  def get_handlers(self):
    return {fn_name.split("_")[1].upper(): getattr(self, fn_name) for fn_name in dir(self) if fn_name.startswith("handle_")}


class DNSProtocol(DNSProtocolClass):
  def __init__(self):
    super(DNSProtocol, self).__init__()
    self.log = logging.getLogger(__name__)
    self.handlers = DNSHandlers(self._myname, self._listen).get_handlers()

  def datagram_received(self, data, addr):
    m = DNSPacket(data)

    # for item in m.question_section:
    #   self.log.info(item)

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
