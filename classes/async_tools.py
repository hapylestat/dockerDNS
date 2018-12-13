# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# Copyright (c) 2018 Reishin <hapy.lestat@gmail.com> and Contributors

import asyncio
import socket


class AsyncIteratorExecutor(object):
  def __init__(self, iterator, loop=None, executor=None):
    """
    :type iterator collections.Iterable
    :type loop asyncio.AbstractEventLoop
    :type executor
    """
    self.__iterator = iterator
    self.__loop = loop or asyncio.get_event_loop()
    self.__executor = executor

  def __aiter__(self):
    return self

  async def __anext__(self):
    value = await self.__loop.run_in_executor(self.__executor, next, self.__iterator, self)

    if value is self:
      raise StopAsyncIteration

    return value


class DNSProtocolClass(asyncio.DatagramProtocol):
  _sock = None
  _myname = None
  _listen = None

  def datagram_received(self, data, addr):
    """Called when some datagram is received."""
    raise NotImplementedError()

  def error_received(self, exc):
    """Called when a send or receive operation raises an OSError.

    (Other than BlockingIOError or InterruptedError.)
    """
    raise NotImplementedError()

  @property
  def sock(self):
    return self._sock


class AsyncDNSSock(object):
  def __init__(self, myname, lister_addr, listern_port, dns_protocol_class):
    """
    :type myname str
    :type listern_port int
    :type lister_addr str
    :type dns_protocol type(DNSProtocolClass)
    """
    self.__myname = myname
    self.__addr = lister_addr
    self.__port = listern_port
    self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.__sock.bind((lister_addr, listern_port))
    self.__dns_protocol_class = dns_protocol_class
    self.__dns_protocol_class._sock = self.__sock
    self.__dns_protocol_class._myname = self.__myname
    self.__dns_protocol_class._listen = self.__addr

  def get_future(self, loop):
    """
    return future for asynio

    :type loop asyncio.AbstractEventLoop
    """
    return loop.create_datagram_endpoint(self.__dns_protocol_class, sock=self.__sock)

  @property
  def sock(self):
    return self.__sock
