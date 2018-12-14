# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# Copyright (c) 2018 Reishin <hapy.lestat@gmail.com> and Contributors


class ContainerKeyStorage(object):
  _name_storage = {}
  _ip_storage = {}

  @classmethod
  def add(cls, container):
    """
    :type container classes.docker_listener.DockerContainerInfo
    """
    cls._name_storage[container.name] = container
    cls._ip_storage[container.ip] = container

  @classmethod
  def get_by_ip(cls, ip: str):
    """
    :rtype classes.docker_listener.DockerContainerInfo
    """
    try:
      return cls._ip_storage[ip]
    except KeyError:
      return None

  @classmethod
  def get_by_name(cls, name: str):
    """
    :rtype classes.docker_listener.DockerContainerInfo|None
    """
    try:
      return cls._name_storage[name]
    except KeyError:
      return None

  @classmethod
  def delete(cls, name: str):
    try:
      ip = cls._name_storage[name].ip
      del cls._name_storage[name]
      del cls._ip_storage[ip]
    except (KeyError, TypeError):
      pass
