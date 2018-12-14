# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# Copyright (c) 2018 Reishin <hapy.lestat@gmail.com> and Contributors

import asyncio


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
