# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
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

question_types = {
  1: "A",
  2: "NS",
  3: "MD",
  4: "MF",
  5: "CNAME",
  6: "SOA",
  7: "MB",
  8: "MG",
  9: "MR",
  10: "NULL",
  11: "WKS",
  12: "PTR",
  13: "HINFO",
  14: "MINFO",
  15: "MX",
  16: "TXT",
  17: "RP",
  18: "AFSDB",
  19: "X25",
  20: "ISDN",
  21: "RT",
  22: "NSAP",
  23: "NSAP-PTR",
  24: "SIG",
  25: "KEY",
  26: "PX",
  27: "GPOS",
  28: "AAAA",
  29: "LOC",
  30: "NXT",
  31: "EID",
  32: "NIMLOC",
  33: "SRV",
  34: "ATMA",
  35: "NAPTR",
  36: "KX",
  37: "CERT",
  38: "A6",
  39: "DNAME",
  40: "SINK",
  41: "OPT",
  42: "APL",
  43: "DS",
  44: "SSHFP",
  45: "IPSECKEY",
  46: "RRSIG",
  47: "NSEC",
  48: "DNSKEY",
  49: "DHCID",
  50: "NSEC3",
  51: "NSEC3PARAM",
  52: "TLSA",
  55: "HIP",
  56: "NINFO",
  57: "RKEY",
  58: "TALINK",
  59: "CDS",
  60: "CDNSKEY",
  61: "OPENPGPKEY",
  62: "CSYNC",
  99: "SPF",
  100: "UINFO",
  101: "UID",
  102: "GID",
  103: "UNSPEC",
  104: "NID",
  105: "L32",
  106: "L64",
  107: "LP",
  108: "EUI48",
  109: "EUI64",
  249: "TKEY",
  250: "TSIG",
  251: "IXFR",
  252: "AXFR",
  253: "MAILB",
  254: "MAILA",
  255: "*",
  256: "URI",
  257: "CAA",
  32768: "TA",
  32769: "DLV",
  65535: "Reserved"
}

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