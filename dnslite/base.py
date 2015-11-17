import struct

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

    #  parse data packet
    self.message_id = _msg[:2]
    _pack1 = int.from_bytes(_msg[2:4], byteorder="big")

    # declare sections
    self.question_section = [None] * int.from_bytes(_msg[4:6], byteorder="big")
    self.answer_section = [None] * int.from_bytes(_msg[6:8], byteorder="big")
    self.authority_section = [None] * int.from_bytes(_msg[8:10], byteorder="big")
    self.additional_section = [None] * int.from_bytes(_msg[10:12], byteorder="big")

    #  decode header section
    self.header = Header(_pack1)

    data_section = _msg[12:]
    for i in range(0, len(self.question_section)):
      item, data_section = QuestionItem.parse(data_section)
      self.question_section[i] = item

      # decode Question section

      # decode Answer section

      # decode Authority section

      # decode Additional section

  def get_question(self, index: int) -> QuestionItem:
    return self.question_section[index]

  def add_answer(self, answer: AnswerItem):
    self.answer_section.append(answer)

  def prepare_answer(self, rcode=RCODE.NO_ERROR):
    self.header.rcode = rcode
    #self.header.aa = FLAG.SET
    #self.header.rd = FLAG.UNSET
    self.header.qr = FLAG.SET

  @property
  def raw(self):
    ret = b""

    ret += self.message_id
    ret += struct.pack(u16bit, self.header.raw)
    #ret += struct.pack(u16bit, len(self.question_section))
    ret += struct.pack(u16bit, 0)
    ret += struct.pack(u16bit, len(self.answer_section))
    ret += struct.pack(u16bit, len(self.authority_section))
    ret += struct.pack(u16bit, len(self.additional_section))

    # for item in self.question_section:
    #   ret += item.raw

    for item in self.answer_section:
      ret += item.raw

    return ret
