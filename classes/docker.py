# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# Copyright (c) 2015 Reishin <hapy.lestat@gmail.com> and Contributors

from docker import Client
from classes.config import Configuration
from classes.logger import alogger


class DockerInfo(object):
  def __init__(self):
    cfg = Configuration.get_instance()
    self.cfg = cfg
    self.log = alogger.getLogger(self.__class__.__name__, self.cfg)
    self.__url = self.cfg.get("docker.url", check_type=str)
    self._conn = Client(self.__url)

  def get_ip_info(self, name: str):
    name = name.split(".")
    try:
      info = self._conn.inspect_container(name[0])
      if info is not None:
        if "NetworkSettings" in info and "IPAddress" in info["NetworkSettings"]:
          return info["NetworkSettings"]["IPAddress"]
    except Exception as e:
      return None
    return None

doker = DockerInfo()