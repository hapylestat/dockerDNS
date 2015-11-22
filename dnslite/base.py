# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# Copyright (c) 2015 Reishin <hapy.lestat@gmail.com> and Contributors

import struct

from dnslite.datapack import bread
from dnslite.types import Header, QuestionItem, AnswerItem
from dnslite.constants import OPCODE, RCODE, FLAG, u16bit


# Book - http://www.zytrax.com/books/dns/ch15/
# https://wiki.python.org/moin/BitManipulation


class DNSPacket(object):
  def __init__(self, _msg):
    """
    :type _msg byte
    :param _msg Get byte array as input and form structured data
    """

    offset = 0

    #  parse data packet
    self.message_id, _msg, offset = bread(_msg, 2, offset)

    _pack1, _msg, offset = bread(_msg, 2, offset, data_fx=lambda x: int.from_bytes(x, byteorder="big"))

    # declare sections
    _size, _msg, offset = bread(_msg, 2, offset, data_fx=lambda x: int.from_bytes(x, byteorder="big"))
    self.question_section = [None] * _size
    # required to store question section offsets for answer_section "name"
    question_offset_grid = [None] * _size

    _size, _msg, offset = bread(_msg, 2, offset, data_fx=lambda x: int.from_bytes(x, byteorder="big"))
    self.answer_section = [None] * _size

    _size, _msg, offset = bread(_msg, 2, offset, data_fx=lambda x: int.from_bytes(x, byteorder="big"))
    self.authority_section = [None] * _size

    _size, _msg, offset = bread(_msg, 2, offset, data_fx=lambda x: int.from_bytes(x, byteorder="big"))
    self.additional_section = [None] * _size

    #  decode header section
    self.header = Header(_pack1)

    # decode Question section
    for i in range(0, len(self.question_section)):
      la = len(_msg)
      item, _msg = QuestionItem.parse(_msg)
      lb = len(_msg)
      question_offset_grid[i] = offset
      self.question_section[i] = item
      offset += la - lb

    # decode Answer section
    for i in range(0, len(self.answer_section)):
      la = len(_msg)
      item, _msg = AnswerItem.parse(_msg)
      lb = len(_msg)

      # here we will get answer name from the offset
      loffset = item.name
      for x in range(0, len(question_offset_grid)):
        if question_offset_grid[x] <= loffset:
          item.name = self.question_section[x].qname

      self.answer_section[i] = item
      offset += la - lb

    # decode Authority section

    # decode Additional section

  def get_question(self, index: int) -> QuestionItem:
    return self.question_section[index]

  def add_answer(self, answer: AnswerItem):
    """
    Add answer item to the list of the answers
    :param answer:
    :return:
    """
    self.answer_section.append(answer)

  def prepare_answer(self, rcode=RCODE.NO_ERROR):
    """
    Prepare dns packet to be sent back to the client
    :param rcode: one of the RCODE variable, represent the status of the query
    :return:
    """
    self.header.rcode = rcode
    self.header.aa = FLAG.SET
    self.header.rd = FLAG.UNSET
    self.header.qr = FLAG.SET

  def raw(self):
    ret = b""
    qoffset = [-1] * len(self.question_section)
    ret += self.message_id
    ret += struct.pack(u16bit, self.header.raw)
    ret += struct.pack(u16bit, len(self.question_section))
    ret += struct.pack(u16bit, len(self.answer_section))
    ret += struct.pack(u16bit, len(self.authority_section))
    ret += struct.pack(u16bit, len(self.additional_section))

    for i in range(0, len(self.question_section)):
      qoffset[i] = len(ret)
      ret += self.question_section[i].raw()

    for i in range(0, len(self.answer_section)):
      offset = qoffset[i] if len(qoffset) >= i else -1
      ret += self.answer_section[i].raw(offset)

    return ret
