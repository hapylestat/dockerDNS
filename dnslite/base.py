

from dnslite.types import Header, QuestionItem, read_byte


class InputMessage(object):
  def __init__(self, _msg):
    """
    :type _msg byte
    :param _msg Get byte array as input and form structured data
    """

    #  parse data packet
    self.message_id = _msg[:2]
    _pack1 = int.from_bytes(_msg[2:4], byteorder="big")
    _qdcount = int.from_bytes(_msg[4:6], byteorder="big")
    _ancount = int.from_bytes(_msg[6:8], byteorder="big")
    _nscount = int.from_bytes(_msg[8:10], byteorder="big")
    _arcount = int.from_bytes(_msg[10:12], byteorder="big")

    # declare sections
    self.question_section = []
    self.answer_section = []
    self.authority_section = []
    self.additional_section = []

    #  decode header section
    self.header = Header(_pack1)

    data_section = _msg[12:]

    for i in range(0, _qdcount):
      count = 1
      domain = []

      while count != 0:
        count, data_section = read_byte(data_section, 1)
        count = int.from_bytes(count, byteorder="big")
        if count != 0:
          domain_part, data_section = read_byte(data_section, count)
          domain.append(domain_part.decode())


      qtype, data_section = read_byte(data_section, 2)
      qtype = int.from_bytes(qtype, byteorder="big")

      qclass, data_section = read_byte(data_section, 2)
      qclass = int.from_bytes(qclass, byteorder="big")

      self.question_section.append(QuestionItem(domain, qtype, qclass))

      # decode Question section

      # decode Answer section

      # decode Authority section

      # decode Additional section