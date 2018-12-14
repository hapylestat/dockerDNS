# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# Copyright (c) 2015 Reishin <hapy.lestat@gmail.com> and Contributors

import struct

from dnslite.constants import u8bit, header_flags, base_len, u16bit, QuestionTypes
import time
import random


# FORMAT HELP:  https://www.ietf.org/rfc/rfc1035.txt


def ip_to_in_addr(ipstring: str, ver: int = 4) -> str:
  if ver == 4:
    ip = ipstring.split(".")
    ip.reverse()
    return ".".join(ip + ["in-addr", "arpa"])


def in_addr_to_ip(in_addr: str, ver: int = 4) -> str:
  if ver == 4:
    ip_block = in_addr.split(".")
    if ".".join(ip_block[-2:]) == "in-addr.arpa":
      ip_block = ip_block[:-2]
      ip_block.reverse()
      return ".".join(ip_block)


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


def generate_message_id() -> bytes:
  random.seed(time.time())
  msgid = random.randrange(1, 39999)
  if msgid.bit_length() <= 16:
    return struct.pack(u16bit, msgid)
  else:
    raise TypeError("Non 16-bit seed used")


def bread(byte_data: bytes, count: int, update_offset: int = None, data_fx=None):
  """
  :param byte_data: bytedata to read
  :param count: count of the data to read
  :param update_offset: if not None, returns tuple -> read_data, rest_data, new_offset
  :param data_fx: apply lambda to the result field
  :return: read_data, rest_data [,new_offset]
  """

  _data = byte_data[:count]

  if data_fx is not None and hasattr(data_fx, '__call__'):
    _data = data_fx(_data)

  if update_offset is not None:
    return _data, byte_data[count:], update_offset + count

  return _data, byte_data[count:]


def make_label(domain: list) -> bytes:
  ret = b""
  for item in domain:
    ret += bytes([len(item)])
    ret += item.encode(encoding="utf-8")

  ret += bytes([0])
  return ret


def pack_a_response(ip) -> tuple:
  if isinstance(ip, str):  # convert ip string xxx.xxx.xxx.xxx to [xxx,xxx,xxx,xxx] of int
    ip = list(map(lambda x: int(x), ip.split(".")))

  if isinstance(ip, list) or isinstance(ip, tuple):  # make sure, that list contain integers
    ip = list(map(lambda x: int(x), ip))

  bdata = b""
  for ipitem in ip:
    bdata += struct.pack(u8bit, ipitem)
  return bdata, len(bdata)


def pack_ptr_response(name) -> tuple:
  if isinstance(name, str):
    name = name.split(".")

  ret = make_label(name)
  return ret, len(ret)


def unpack_a_response(data: bytes) -> list:
  ret = [-1] * 4
  for i in range(0, 4):
    octet, data = bread(data, 1, data_fx=lambda x: int.from_bytes(x, byteorder="big"))
    ret[i] = octet

  return ret


def unpack_ptr_response(data: bytes) -> str:
  size = -1
  _str = []
  while size != 0:  # ToDo: add check if packet is malformed and no zero flag at the end
    size, data = bread(data, 1, data_fx=lambda x: int.from_bytes(x, byteorder="big"))
    if size != 0:
      lbl, data = bread(data, size)
      try:
        _str.append(lbl.decode(encoding="utf-8"))
      except UnicodeDecodeError:
        _str.append("<invalid format>")

  return ".".join(_str)


def pack_txt_response(name) -> tuple:
  bname = str(name).encode("UTF-8")
  ret = bytes([len(bname)]) + str(name).encode("UTF-8")
  return ret, len(ret)


def unpack_txt_response(data: bytes) -> str:
  raise NotImplementedError()


# register packer/unpacker
QuestionTypes.set_fx("A", pack_a_response, unpack_a_response)
QuestionTypes.set_fx("PTR", pack_ptr_response, unpack_ptr_response)
QuestionTypes.set_fx("NS", pack_ptr_response, unpack_ptr_response)
QuestionTypes.set_fx("TXT", pack_txt_response, unpack_txt_response)
