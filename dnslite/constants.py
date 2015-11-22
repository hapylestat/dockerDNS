# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# Copyright (c) 2015 Reishin <hapy.lestat@gmail.com> and Contributors


class RCODE(object):
  NO_ERROR = 0
  FORMAT_ERROR = 1
  SERVER_FAILURE = 2
  NAME_ERROR = 3
  NOT_IMPLEMENTED = 4
  REFUSED = 5


class OPCODE(object):
  QUERY = 0
  IQUERY = 1
  STATUS = 2


class FLAG(object):
  SET = 1
  UNSET = 0


class QuestionTypeItem(object):
  def __init__(self, qtype: int=None, qname: str=None, fx_pack=None, fx_unpack=None):
    self.qtype = qtype
    self.qname = qname
    self.fx_pack = fx_pack
    self.fx_unpack = fx_unpack


class QuestionTypes(object):
  __types = {}
  __names = {}

  @classmethod
  def add(cls, q):
    if isinstance(q, QuestionTypeItem):
      cls.__types[q.qtype] = q
      cls.__names[q.qname] = q
    elif isinstance(q, list):
      for item in q:
        cls.add(item)

  @classmethod
  def get(cls, attr) -> QuestionTypeItem:
    if isinstance(attr, int) and attr in cls.__types:
      return cls.__types[attr]
    elif isinstance(attr, str) and attr in cls.__names:
      return cls.__names[attr]
    else:
      return None

  @classmethod
  def set_fx(cls, attr, fx_pack=None, fx_unpack=None):
    if isinstance(attr, int) and attr in cls.__types:
      cls.__types[attr].fx_pack = fx_pack
      cls.__types[attr].fx_unpack = fx_unpack
    elif isinstance(attr, str) and attr in cls.__names:
      cls.__names[attr].fx_pack = fx_pack
      cls.__names[attr].fx_unpack = fx_unpack
    else:
      return None

  @classmethod
  def pack(cls, attr, data) -> tuple:
    """
    :param attr: record to pack
    :param data: data to pack
    :return: tuple(packet_data, len)
    :rtype tuple(bytes, int)
    """
    r = cls.get(attr)
    if r is not None and r.fx_pack is not None:
      return r.fx_pack(data)
    else:
      return None

  @classmethod
  def unpack(cls, attr, data):
    """
    :param attr: record to pack
    :param data: data to pack
    :return: tuple(packet_data, len)
    :rtype tuple(bytes, int)
    """
    r = cls.get(attr)
    if r is not None and r.fx_unpack is not None:
      return r.fx_unpack(data)
    else:
      return None, None

u16bit = ">H"
u32bit = ">I"
u8bit = ">B"

__four_bytes_mask = 0b1111
__one_byte_mask = 0b1
base_len = 16
header_flags = {
  "qr": [0, __one_byte_mask],
  "opcode": [1, __four_bytes_mask],  # 16 bytes
  "aa": [5, __one_byte_mask],
  "tc": [6, __one_byte_mask],
  "rd": [7, __one_byte_mask],
  "ra": [8, __one_byte_mask],
  "res1": [9, __one_byte_mask],
  "res2": [10, __one_byte_mask],
  "res3": [11, __one_byte_mask],
  "rcode": [12, __four_bytes_mask]
}

# http://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml
QuestionTypes.add([
  QuestionTypeItem(1, "A"),
  QuestionTypeItem(2, "NS"),
  QuestionTypeItem(3, "MD"),
  QuestionTypeItem(4, "MF"),
  QuestionTypeItem(5, "CNAME"),
  QuestionTypeItem(6, "SOA"),
  QuestionTypeItem(7, "MB"),
  QuestionTypeItem(8, "MG"),
  QuestionTypeItem(9, "MR"),
  QuestionTypeItem(10, "NULL"),
  QuestionTypeItem(11, "WKS"),
  QuestionTypeItem(12, "PTR"),
  QuestionTypeItem(13, "HINFO"),
  QuestionTypeItem(14, "MINFO"),
  QuestionTypeItem(15, "MX"),
  QuestionTypeItem(16, "TXT"),
  QuestionTypeItem(17, "RP"),
  QuestionTypeItem(18, "AFSDB"),
  QuestionTypeItem(19, "X25"),
  QuestionTypeItem(20, "ISDN"),
  QuestionTypeItem(21, "RT"),
  QuestionTypeItem(22, "NSAP"),
  QuestionTypeItem(23, "NSAP-PTR"),
  QuestionTypeItem(24, "SIG"),
  QuestionTypeItem(25, "KEY"),
  QuestionTypeItem(26, "PX"),
  QuestionTypeItem(27, "GPOS"),
  QuestionTypeItem(28, "AAAA"),
  QuestionTypeItem(29, "LOC"),
  QuestionTypeItem(30, "NXT"),
  QuestionTypeItem(31, "EID"),
  QuestionTypeItem(32, "NIMLOC"),
  QuestionTypeItem(33, "SRV"),
  QuestionTypeItem(34, "ATMA"),
  QuestionTypeItem(35, "NAPTR"),
  QuestionTypeItem(36, "KX"),
  QuestionTypeItem(37, "CERT"),
  QuestionTypeItem(38, "A6"),
  QuestionTypeItem(39, "DNAME"),
  QuestionTypeItem(40, "SINK"),
  QuestionTypeItem(41, "OPT"),
  QuestionTypeItem(42, "APL"),
  QuestionTypeItem(43, "DS"),
  QuestionTypeItem(44, "SSHFP"),
  QuestionTypeItem(45, "IPSECKEY"),
  QuestionTypeItem(46, "RRSIG"),
  QuestionTypeItem(47, "NSEC"),
  QuestionTypeItem(48, "DNSKEY"),
  QuestionTypeItem(49, "DHCID"),
  QuestionTypeItem(50, "NSEC3"),
  QuestionTypeItem(51, "NSEC3PARAM"),
  QuestionTypeItem(52, "TLSA"),
  QuestionTypeItem(55, "HIP"),
  QuestionTypeItem(56, "NINFO"),
  QuestionTypeItem(57, "RKEY"),
  QuestionTypeItem(58, "TALINK"),
  QuestionTypeItem(59, "CDS"),
  QuestionTypeItem(60, "CDNSKEY"),
  QuestionTypeItem(61, "OPENPGPKEY"),
  QuestionTypeItem(62, "CSYNC"),
  QuestionTypeItem(99, "SPF"),
  QuestionTypeItem(100, "UINFO"),
  QuestionTypeItem(101, "UID"),
  QuestionTypeItem(102, "GID"),
  QuestionTypeItem(103, "UNSPEC"),
  QuestionTypeItem(104, "NID"),
  QuestionTypeItem(105, "L32"),
  QuestionTypeItem(106, "L64"),
  QuestionTypeItem(107, "LP"),
  QuestionTypeItem(108, "EUI48"),
  QuestionTypeItem(109, "EUI64"),
  QuestionTypeItem(249, "TKEY"),
  QuestionTypeItem(250, "TSIG"),
  QuestionTypeItem(251, "IXFR"),
  QuestionTypeItem(252, "AXFR"),
  QuestionTypeItem(253, "MAILB"),
  QuestionTypeItem(254, "MAILA"),
  QuestionTypeItem(255, "*"),
  QuestionTypeItem(256, "URI"),
  QuestionTypeItem(257, "CAA"),
  QuestionTypeItem(32768, "TA"),
  QuestionTypeItem(32769, "DLV"),
  QuestionTypeItem(65535, "-")
])
