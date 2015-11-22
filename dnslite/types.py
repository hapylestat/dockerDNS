# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# Copyright (c) 2015 Reishin <hapy.lestat@gmail.com> and Contributors


from dnslite.constants import QuestionTypes, u16bit, u32bit, FLAG
import struct

from dnslite.datapack import make_label, bread, get_bit, set_bit


class QuestionItem(object):
  def __init__(self, qname, qtype: int, qclass: int):
    """
    :param qname: question subject
    :param qtype: question type
    :param qclass: question class
    :return:
    """
    if isinstance(qname, str) and qtype == 1:
      qname = qname.split(".")

    self._qname = qname
    self._qtype = int(qtype)
    self._qclass = qclass
    self._qtype_str = QuestionTypes.get(qtype).qname

  @property
  def qname(self) -> list:
    return self._qname

  @property
  def qname_str(self) -> str:
    return ".".join(self._qname)

  @property
  def qtype(self) -> int:
    return self._qtype

  @property
  def qclass(self) -> int:
    return self._qclass

  @property
  def qtype_name(self) -> str:
    return self._qtype_str

  def __str__(self):
    return "name: %s; type: %s (%s); class: %s" % (".".join(self.qname), self.qtype_name, self.qtype, self.qclass)

  def raw(self) -> bytes:
    b = b""
    b += make_label(self._qname)
    b += struct.pack(u16bit, self._qtype)
    b += struct.pack(u16bit, self._qclass)

    return b

  def get_answer(self, data=None, atype=None):
    """
    :rtype AnswerItem
    """
    if atype is None:
      atype = self._qtype

    return AnswerItem(self, rtype=atype, data=data)

  @staticmethod
  def parse(bytedata: bytes) -> tuple:
    """
    :param bytedata data, from the dns packet stream
    :return: tuple(QuestionItem, rest of bytedata)
    :rtype QuestionItem, bytes
    """
    domain = []
    count = -1

    while count != 0:
      count, bytedata = bread(bytedata, 1)
      count = int.from_bytes(count, byteorder="big")
      if count != 0:
        domain_part, bytedata = bread(bytedata, count)
        domain.append(domain_part.decode())

    qtype, bytedata = bread(bytedata, 2)
    qtype = int.from_bytes(qtype, byteorder="big")

    qclass, bytedata = bread(bytedata, 2)
    qclass = int.from_bytes(qclass, byteorder="big")

    return QuestionItem(domain, qtype, qclass), bytedata


class AnswerItem(object):
  def __init__(self, question: QuestionItem, rtype=None, data=None, ttl=2800):
    self._q = question
    self.__fqdn = False
    self._name = question.qname
    self._type = question.qtype  # u16bit
    self._class = question.qclass  # u16bit
    self._ttl = ttl  # u32bit
    self._data = data
    self._rtype = rtype

  def make_response(self, _type: int, data):
    self._data = data
    self._rtype = _type

  @property
  def ttl(self):
    return self._ttl

  @property
  def atype(self):
    return self._type

  @property
  def value(self):
    return self._data

  @property
  def name(self):
    return self._name

  @name.setter
  def name(self, value):
    self._name = value

  def raw(self, offset):
    """
    :param offset: offset from begin of the message for the name label
    :return:
    """
    body = b""

    if offset < 1:
      offset = 0

    body += struct.pack(u16bit, 0b1100000000000000 + offset)  # 16 bytes record, type 11, start 2 bytes
    body += struct.pack(u16bit, self._type)
    body += struct.pack(u16bit, self._class)
    body += struct.pack(u32bit, self._ttl)
    ipdata, size = QuestionTypes.pack(self._rtype, self._data)

    if ipdata is None:
      return None

    body += struct.pack(u16bit, size)
    body += ipdata
    return body

  @staticmethod
  def parse(bytedata: bytes) -> tuple:
    """
    :param bytedata data, from the dns packet stream
    :return: tuple(AnswerItem, rest of bytedata)
    :rtype AnswerItem, bytes
    """

    name_field, bytedata = bread(bytedata, 2)
    name_field = int.from_bytes(name_field, byteorder="big")

    # 0bXY00000000000000 - X: 1 Y: 1 -> 11, X:0 Y:1 -> 1, X:1 Y:0 -> 10
    name_type = 10 * ((name_field >> 15) & 0b1) + ((name_field >> 14) & 0b1)
    name_offset = name_field & 0b001111111111111

    assert name_type == 11

    _type, bytedata = bread(bytedata, 2)
    _type = int.from_bytes(_type, byteorder="big")

    _class, bytedata = bread(bytedata, 2)
    _class = int.from_bytes(_class, byteorder="big")

    _ttl, bytedata = bread(bytedata, 4)
    _ttl = int.from_bytes(_ttl, byteorder="big")

    rdlen, bytedata = bread(bytedata, 2)
    rdlen = int.from_bytes(rdlen, byteorder="big")

    rddata, bytedata = bread(bytedata, rdlen)
    rddata = QuestionTypes.unpack(_type, rddata)

    return AnswerItem(QuestionItem(name_offset, _type, _class), _type, rddata, _ttl), bytedata


class Header(object):
  def __init__(self, bin_content=None):
    self.qr = FLAG.UNSET
    self.opcode = FLAG.UNSET
    self.aa = FLAG.UNSET
    self.tc = FLAG.UNSET
    self.rd = FLAG.UNSET
    self.ra = FLAG.UNSET
    self.res1 = FLAG.UNSET
    self.res2 = FLAG.UNSET
    self.res3 = FLAG.UNSET
    self.rcode = FLAG.UNSET

    if bin_content is not None:
      self.__init_from_bin(bin_content)

  def __init_from_bin(self, bin_content):
    self.qr = get_bit(bin_content, "qr")
    self.opcode = get_bit(bin_content, "opcode")
    self.aa = get_bit(bin_content, "aa")
    self.tc = get_bit(bin_content, "tc")
    self.rd = get_bit(bin_content, "rd")
    self.ra = get_bit(bin_content, "ra")
    self.res1 = get_bit(bin_content, "res1")
    self.res2 = get_bit(bin_content, "res2")
    self.res3 = get_bit(bin_content, "res3")
    self.rcode = get_bit(bin_content, "rcode")

  @property
  def raw(self):
    ret = 0
    ret = set_bit(ret, "qr", self.qr)
    ret = set_bit(ret, "opcode", self.opcode)
    ret = set_bit(ret, "aa", self.aa)
    ret = set_bit(ret, "tc", self.tc)
    ret = set_bit(ret, "rd", self.rd)
    ret = set_bit(ret, "ra", self.ra)
    ret = set_bit(ret, "res1", self.res1)
    ret = set_bit(ret, "res2", self.res2)
    ret = set_bit(ret, "res3", self.res3)
    ret = set_bit(ret, "rcode", self.rcode)
    return ret

  def __str__(self):
    out = ""
    for field in self.__dir__():
      if field[:1] != "_" and field[:2] != "__" and not hasattr(self.__getattribute__(field), "__call__"):
        out += "%s: %s\n" % (field, self.__getattribute__(field))
    return out

