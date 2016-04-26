# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# Copyright (c) 2015 Reishin <hapy.lestat@gmail.com> and Contributors

from docker import Client
from appcore.core import config
from appcore.core import aLogger


class DockerInfo(object):
  def __init__(self):
    cfg = config.get_instance()
    self.cfg = cfg
    self.log = aLogger.getLogger(self.__class__.__name__, self.cfg)
    self.__url = self.cfg.get("docker.url", check_type=str)
    self._conn = Client(self.__url)

  def get_ip_info(self, name: str):
    name = name.split(".")
    try:
      info = self._conn.inspect_container(name[0])
      if info is not None and "NetworkSettings" in info and "IPAddress" in info["NetworkSettings"]:
          return info["NetworkSettings"]["IPAddress"] if info["NetworkSettings"]["IPAddress"].strip() != "" else None
    except Exception as e:
      return None
    return None

  def container_name_by_ip(self, ip:str):
    containerIDS = self._conn.containers()
    for containerID in containerIDS:
      container_obj = self._conn.inspect_container(containerID)
      if container_obj is not None and "NetworkSettings" in container_obj and "IPAddress" in container_obj["NetworkSettings"]:
        container_ip = container_obj["NetworkSettings"]["IPAddress"] if container_obj["NetworkSettings"]["IPAddress"].strip() else None
        if container_ip == ip:
          return "%s.%s" % (container_obj["Config"]["Hostname"], container_obj["Config"]["Domainname"])




doker = DockerInfo()
