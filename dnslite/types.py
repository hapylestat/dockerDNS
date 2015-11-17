

from dnslite.constants import question_types, header_flags, base_len, u16bit, u32bit, u8bit
import struct


def ip_to_in_addr(ipstring: str, ver: int = 4) -> str:
  if ver == 4:
    ip = ipstring.split(".")
    ip.reverse()
    return ".".join(ip + ["in-addr", "arpa"])


def get_bit(_bitfield, name):
  _bit_mask = header_flags[name][1]
  _bit_len = _bit_mask.bit_length()
  _bit_pos = base_len - header_flags[name][0] - _bit_len

  return (_bitfield >> _bit_pos) & _bit_mask


def set_bit(_bitfield, name, value=0b1):
  _bit_mask = header_flags[name][1]
  _bit_len = _bit_mask.bit_length()
  _bit_pos = base_len - header_flags[name][0] - _bit_len

  return _bitfield | (value << _bit_pos)


def read_byte(byte_data, count):
  return byte_data[:count], byte_data[count:]


def make_label(domain: list) -> bytes:
  ret = b""
  for item in domain:
    ret += bytes([len(item)])
    ret += item.encode(encoding="utf-8")

  ret += bytes([0])
  return ret


class QuestionItem(object):
  def __init__(self, qname, qtype, qclass):
    self._qname = qname
    self._qtype = int(qtype)
    self._qclass = qclass
    self._qtype_str = question_types[qtype] if qtype in question_types else qtype

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

  @property
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
      count, bytedata = read_byte(bytedata, 1)
      count = int.from_bytes(count, byteorder="big")
      if count != 0:
        domain_part, bytedata = read_byte(bytedata, count)
        domain.append(domain_part.decode())

    qtype, bytedata = read_byte(bytedata, 2)
    qtype = int.from_bytes(qtype, byteorder="big")

    qclass, bytedata = read_byte(bytedata, 2)
    qclass = int.from_bytes(qclass, byteorder="big")

    return QuestionItem(domain, qtype, qclass), bytedata


class AnswerItem(object):
  def __init__(self, question: QuestionItem, rtype=None, data=None):
    self._q = question
    self.__fqdn = False
    self._name = question.qname[0] if len(question.qname) > 0 else ""
    self._type = question.qtype  # u16bit
    self._class = question.qclass  # u16bit
    self._ttl = 2800  # u32bit
    self._data = data
    self._rtype = rtype

  def make_response(self, _type: int, data):
    self._data = data
    self._rtype = _type

  @property
  def raw(self):
    body = b""
    body += struct.pack(u16bit, 0b1100000000000010)  # 16 bytes record, type 11, start 2 bytes

    body += make_label(self._q.qname)
    body += struct.pack(u16bit, self._type)
    body += struct.pack(u16bit, self._class)
    body += struct.pack(u32bit, self._ttl)

    ipdata = None
    size = None
    if self._rtype == 1:  # A record
      ipdata, size = self.__get_a_response(self._data)
    elif self._rtype == 12:  # PTR record
      ipdata, size = self.__get_ptr_response(self._data)

    if ipdata is None:
      return None

    body += struct.pack(u16bit, size)
    body += ipdata
    return body

  def __get_a_response(self, ip) -> tuple:
    if isinstance(ip, str):  # convert ip string xxx.xxx.xxx.xxx to [xxx,xxx,xxx,xxx] of int
      ip = list(map(lambda x: int(x), ip.split(".")))

    if isinstance(ip, list) or isinstance(ip, tuple):  # make sure, that list contain integers
      ip = list(map(lambda x: int(x), ip))

    bdata = b""
    for ipitem in ip:
      bdata += struct.pack(u8bit, ipitem)
    return bdata, len(bdata)

  def __get_ptr_response(self, name) -> tuple:
    if isinstance(name, str):
      name = name.split(".")

    ret = make_label(name)
    return ret, len(ret)


class Header(object):
  def __init__(self, bin_content):
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

