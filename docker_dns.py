#!/usr/bin/python3

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# Copyright (c) 2015 Reishin <hapy.lestat@gmail.com> and Contributors


from classes.async_tools import AsyncDNSSock
from apputils.core import Configuration

from classes.dns_listener import DNSProtocol
from classes.docker_listener import DockerListener

import logging
import asyncio


conf = Configuration()


logging.basicConfig(level=logging.INFO, format='%(threadName)s %(message)s')

log = logging.getLogger(__name__)
listen = conf.get("listen", default="127.0.0.1", check_type=str)
port = conf.get("port", default=53, check_type=int)
myname = conf.get("myname", default="FakeServer", check_type=str)


def main():
  loop = asyncio.get_event_loop()
  docker_listener = DockerListener(conf.get("docker"))

  futures = docker_listener.get_futures()

  log.info("Start listening on udp %s:%s", listen, port)
  futures.append(AsyncDNSSock(myname, listen, port, DNSProtocol).get_future(loop))

  loop.run_until_complete(asyncio.gather(*futures))
  loop.run_forever()


if __name__ == '__main__':
  main()
