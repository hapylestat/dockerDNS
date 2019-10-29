# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# Copyright (c) 2018 Reishin <hapy.lestat@gmail.com> and Contributors

import asyncio
import logging
from dataclasses import dataclass

from docker import APIClient as Client
from classes.async_tools import AsyncIteratorExecutor
from classes.storage import ContainerKeyStorage


@dataclass
class DockerContainerInfo(object):
  name: str = None
  ip: str = None
  docker: int = None


class DockerActions(object):
  kill = "kill"
  die = "die"
  stop = "stop"
  start = "start"


class DockerListener(object):
  def __init__(self, uris):
    """
    :type uris list[str]
    """
    self._log = logging.getLogger(__name__)
    self._dockers = []
    self._docker_to_update = []

    for i in range(len(uris)):
      try:
        self._dockers.append(Client(uris[i]))
        self._docker_to_update.append(i)
      except Exception as e:
        self._log.error("Failed to initialize docker with url '{}' : {}".format(uris[i], str(e)))

  def __load_docker_container_state(self, docker_index: int):
    try:
      self._log.info("Fetching container information from {}".format(self._dockers[docker_index].base_url))
      for container in self._dockers[docker_index].containers(all=True):
        if container["State"] != "running":
          continue
        name = container['Names'][0].partition("/")[2].strip()
        ip = container["NetworkSettings"]["Networks"]["bridge"]["IPAddress"].strip()
        ContainerKeyStorage.add(DockerContainerInfo(name=name, ip=ip, docker=docker_index))
    except:
      self._log.warning("Failed to get container info from {}".format(self._dockers[docker_index].base_url))
      raise

  async def __offline_docker_updater(self):
    while True:
      if self._docker_to_update:
        check_list = list(self._docker_to_update)
        self._docker_to_update = []
        while check_list:
          i = check_list.pop(0)
          try:
            self.__load_docker_container_state(i)
          except:
            self._docker_to_update.append(i)
      await asyncio.sleep(30)

  async def __read_docker_events(self, docker_index):
    """
    :type docker_index int
    """
    docker = self._dockers[docker_index]
    while True:
      try:
        if docker_index in self._docker_to_update:
          await asyncio.sleep(0.5)
          continue

        self._log.info("Subscribing to server {} events".format(docker.base_url))
        async for event in AsyncIteratorExecutor(docker.events(decode=True)):
          if event["Type"] != "container":
            continue

          name = event["Actor"]["Attributes"]["name"]
          action = event["Action"]

          if action in (DockerActions.die, DockerActions.kill, DockerActions.stop):
            ContainerKeyStorage.delete(name)
            self._log.info("Removing '{}' container from the cache".format(name))
          elif action == DockerActions.start:
            info = docker.inspect_container(name)
            ip = None
            if info is not None and "NetworkSettings" in info and "IPAddress" in info["NetworkSettings"]:
              ip = info["NetworkSettings"]["IPAddress"] if info["NetworkSettings"]["IPAddress"].strip() != "" else None

            ContainerKeyStorage.add(DockerContainerInfo(name=name, ip=ip, docker=docker_index))
            self._log.info("Adding '{}' container to cache with ip: {}".format(name, ip))
      except:
        self._log.error("Failed to subscribe to server {} events".format(docker.base_url))
        await asyncio.sleep(30)
        if docker_index not in self._docker_to_update:
          self._docker_to_update.append(docker_index)

  def get_futures(self):
    return [self.__read_docker_events(docker) for docker in range(len(self._dockers))] + [self.__offline_docker_updater()]


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




