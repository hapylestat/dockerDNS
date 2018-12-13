# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# Copyright (c) 2015 Reishin <hapy.lestat@gmail.com> and Contributors
import logging
from dataclasses import dataclass

from docker import APIClient as Client
from classes.async_tools import AsyncIteratorExecutor


@dataclass
class DockerContainerInfo(object):
  name: str = None
  ip: str = None
  dccker: str = None


class DockerListener(object):
  def __init__(self, uris):
    """
    :type uris list[str]
    """
    self._log = logging.getLogger(__name__)
    self._dockers = []
    for url in uris:
      try:
        self._dockers.append(Client(url))
      except Exception as e:
        self._log.error("Failed to initialize docker with url '{}' : {}".format(url, str(e)))

  async def __read_docker_events(self, docker_index):
    """
    :type docker int
    """
    docker = self._dockers[docker_index]
    async for event in AsyncIteratorExecutor(docker.events(decode=True)):
      print(event)

  def get_futures(self):
    return [self.__read_docker_events(docker) for docker in range(len(self._dockers))]


class DockerInfo(object):
  def __init__(self, url):
    """
    :type url str
    """
    self.__url = url
    self._conn = Client(self.__url)

  def ping(self):
    return self._conn.ping()

  def get_ip_info(self, name: str):
    name, _, _ = name.partition(".")
    try:
      info = self._conn.inspect_container(name)
      if info is not None and "NetworkSettings" in info and "IPAddress" in info["NetworkSettings"]:
        return info["NetworkSettings"]["IPAddress"] if info["NetworkSettings"]["IPAddress"].strip() != "" else None
    except Exception:
      return None
    return None

  def container_name_by_ip(self, ip:str):
    container_ids = self._conn.containers()
    for container_id in container_ids:
      container_obj = self._conn.inspect_container(container_id)
      if container_obj is not None and "NetworkSettings" in container_obj and "IPAddress" in container_obj["NetworkSettings"]:
        container_ip = container_obj["NetworkSettings"]["IPAddress"] if container_obj["NetworkSettings"]["IPAddress"].strip() else None
        if container_ip == ip:
          return "%s.%s" % (container_obj["Config"]["Hostname"], container_obj["Config"]["Domainname"])




