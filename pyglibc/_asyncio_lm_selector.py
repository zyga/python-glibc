# Copyright 2014 Canonical Ltd.
# Written by:
#   Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
:mod:`pyglibc._asyncio_selector` -- Selector mechanics
======================================================
"""
from __future__ import absolute_import

import collections
import logging

from pyglibc import selectors
from pyglibc._modular import multiplexed

__author__ = 'Zygmunt Krynicki <zygmunt.krynicki@canonical.com>'
__all__ = [
    'lm_selector',
]

_logger = logging.getLogger('asyncio')


io_handler = collections.namedtuple(
    "io_handler", "fd callback args")


class lm_selector(object):

    @multiplexed
    def __init__(self, **kwargs):
        _logger.debug("Setting up I/O event selector")
        self.__selector = selectors.DefaultSelector()
        self.__readers = {}
        self.__writers = {}

    @multiplexed(inversed=True)
    def close(self):
        _logger.debug("Shutting down I/O event selector")
        self.__selector.close()
        self.__readers.clear()
        self.__writers.clear()

    def add_reader(self, fd, callback, *args):
        # Figure out the effective flags for this fd
        events = selectors.EVENT_READ
        if fd in self.__writers:
            events |= selectors.EVENT_WRITE
        self.__readers[fd] = io_handler(fd, callback, args)
        # See if it's already registered and if so, modify the current
        if fd not in self.__selector.get_map():
            self.__selector.register(fd, events)
        else:
            self.__selector.modify(fd, events)

    def remove_reader(self, fd):
        if fd not in self.__readers:
            return False
        if fd in self.__writers:
            self.__selector.modify(fd, selectors.EVENT_WRITE)
        else:
            self.__selector.unregister(fd)
        del self.__readers[fd]
        return True

    def add_writer(self, fd, callback, *args):
        # Figure out the effective flags for this fd
        events = selectors.EVENT_WRITE
        if fd in self.__readers:
            events |= selectors.EVENT_READ
        self.__writers[fd] = io_handler(fd, callback, args)
        # See if it's already registered and if so, modify the current
        if fd not in self.__selector.get_map():
            self.__selector.register(fd, events)
        else:
            self.__selector.modify(fd, events)

    def remove_writer(self, fd):
        if fd not in self.__writers:
            return False
        if fd in self.__readers:
            self.__selector.modify(fd, selectors.EVENT_READ)
        else:
            self.__selector.unregister(fd)
        del self.__writers[fd]
        return True

    def _run_once(self):
        """
        Run one iteration of the loop.
        """
        _logger.debug("Starting loop iteration")
        t_started = t_wait_started = self.time()
        keys_and_events_list = self.__selector.select(None)
        t_wait_done = t_io_started = self.time()
        self.__process_key_and_events_list(keys_and_events_list)
        t_done = t_io_done = self.time()
        _logger.debug((
            "Loop iteration finished:\n"
            "\tsleeping:   %f\n"
            "\tprocessing: %f\n"
            "\ttotal:      %f"),
            t_wait_done - t_wait_started,
            t_io_done - t_io_started,
            t_done - t_started)

    def __process_key_and_events_list(self, keys_and_events_list):
        for key, events in keys_and_events_list:
            self.__process_key_and_events(key, events)

    def __process_key_and_events(self, key, events):
        if events & selectors.EVENT_READ:
            self.__process_read(key)
        if events & selectors.EVENT_WRITE:
            self.__process_write(key)

    def __process_read(self, key):
        try:
            handler = self.__readers[key.fd]
        except KeyError:
            _logger.error(
                "Received EVENT_READ but there's no read handler?")
        else:
            _logger.debug("Dispatching reaction to EVENT_READ on %s", key)
            _logger.debug("Handler callback: %r", handler.callback)
            _logger.debug("Handler arguments: %r", handler.args)
            handler.callback(*handler.args)

    def __process_write(self, key):
        try:
            handler = self.__writers[key.fd]
        except KeyError:
            _logger.error(
                "Received EVENT_WRITE but there's no read handler?")
        else:
            _logger.debug("Dispatching reaction to EVENT_WRITE on %s", key)
            _logger.debug("Handler callback: %r", handler.callback)
            _logger.debug("Handler arguments: %r", handler.args)
            handler.callback(*handler.args)
