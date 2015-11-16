

from dnslite.constants import question_types, header_flags, base_len


class QuestionItem(object):
  def __init__(self, qname, qtype, qclass):
    self.qname = qname
    self.qtype = qtype
    self.qclass = qclass

    self.qtype_str = question_types[qtype] if qtype in question_types else qtype

  def __str__(self):
    return "name: %s; type: %s (%s); class: %s" % (".".join(self.qname), self.qtype_str, self.qtype, self.qclass)


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

  def __str__(self):
    out = ""
    for field in self.__dir__():
      if field[:1] != "_" and field[:2] != "__" and not hasattr(self.__getattribute__(field), "__call__"):
        out += "%s: %s\n" % (field, self.__getattribute__(field))
    return out


def get_bit(_bitfield, name):
  _bit_pos = base_len - header_flags[name][0]
  _bit_mask = header_flags[name][1]
  return (_bitfield >> _bit_pos) & _bit_mask


def read_byte(byte_data, count):
  return byte_data[:count], byte_data[count:]
