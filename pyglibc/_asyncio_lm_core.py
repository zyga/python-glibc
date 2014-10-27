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
:mod:`pyglibc._asyncio_lm_core` -- Core methods of theloop API
==============================================================
"""
from __future__ import absolute_import

import abc
import logging

from pyglibc._abc import Interface
from pyglibc._asyncio_errors import InvalidStateError
from pyglibc._modular import multiplexed

__author__ = 'Zygmunt Krynicki <zygmunt.krynicki@canonical.com>'
__all__ = [
    'lm_core',
]


_logger = logging.getLogger('asyncio')


class lm_core_dependencies(Interface):
    """
    Interface containing dependencies of the :class:`lm_core` class.
    """

    @abc.abstractmethod
    def _run_once(self):
        """
        do at most one iteration of the loop
        """


class lm_core(object):
    """
    Loop module for core loop operations
    """

    @multiplexed
    def __init__(self):
        _logger.debug("Setting up core event loop mechanics")
        self.__is_running = False
        self.__should_run = False
        self.__closed = False

    def run_forever(self):
        """
        Run the event loop until :meth:`stop()` is called.

        :raises InvalidStateError:
            If the loop is already running
        """
        _logger.debug("Running the event loop forever")
        self.__should_run = True
        self.__started()
        try:
            while self.__should_run:
                self._run_once()
        finally:
            self.__stopped()

    def run_until_complete(self, future):
        """
        Run the event loop until the future is done.

        :param future:
            A :class:`Future` to wait for
        :raises InvalidStateError:
            If the loop is already running
        :raises RuntimeError:
            If the loop was stopped prematurely and the future is not done.
            This is not defined by :PEP:`3156`.
            This is done for compatibility with python3.4.

        The event loop may be stopped earlier by calling :meth:`stop()`.
        """
        _logger.debug("%s.run_complete_forever()", 'lm_core')
        self.__should_run = True
        self.__started()
        try:
            while self.__should_run:
                self._run_once()
                if future.done():
                    self._should_run = False
        finally:
            self.__stopped()
        if not future.done():
            raise RuntimeError("loop stopped prematurely, future not done")

    @multiplexed
    def stop(self):
        """
        Stop the event loop as soon as possible.

        It is fine to restart the loop to run again with :meth:`run_forever()`
        or :meth:`run_until_complete()`. No callbacks are lost.
        """
        self.__should_run = False

    def is_closed(self):
        """
        Check if the loop is closed.

        :returns:
            True if the loop is closed.

        A closed loop cannot be used for anything
        """
        return self.__closed

    def is_running(self):
        """
        Check if the loop is running.

        :returns:
            True if the loop is running, False otherwise.
        """
        return self.__is_running

    @multiplexed(inversed=True)
    def close(self):
        """
        Close the event loop.

        :raises InvalidStateError:
            If the loop is currently running
        """
        _logger.debug("%s.close()", 'lm_core')
        if self.__is_running:
            raise InvalidStateError((
                "EventLoop.close() cannot be called while"
                " the loop is running."))
        self.__closed = True

    def __started(self):
        self.__is_running = True

    def __stopped(self):
        self.__is_running = False
