# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# Copyright (c) 2015 Reishin <hapy.lestat@gmail.com> and Contributors

from docker import APIClient as Client


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
