#!/usr/bin/python3.7

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# Copyright (c) 2015 Reishin <hapy.lestat@gmail.com> and Contributors
import socket

from apputils.core import Configuration

from classes.dns_listener import DNSProtocol
from classes.docker_listener import DockerListener

import logging
import asyncio


conf = Configuration()


logging.basicConfig(level=logging.INFO, format='%(threadName)s %(message)s')

log = logging.getLogger(__name__)
listen = conf.get("listen", default=["127.0.0.1:53"], check_type=list)
myname = conf.get("myname", default="FakeServer", check_type=str)


def main():
  loop = asyncio.get_event_loop()
  docker_listener = DockerListener(conf.get("docker"))
  DNSProtocol._name = myname

  futures = docker_listener.get_futures()

  for l in listen:
    ip, _, port = l.partition(":")
    if not port:
      port = 53

    port = int(port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((ip, port))

    futures.append(loop.create_datagram_endpoint(DNSProtocol, sock=sock))

  loop.run_until_complete(asyncio.gather(*futures))
  loop.run_forever()


if __name__ == '__main__':
  main()
