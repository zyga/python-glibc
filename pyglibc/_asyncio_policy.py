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
:mod:`pyglibc._asyncio_policy` -- PEP3156 event loop policy APIs
================================================================
"""
from __future__ import absolute_import

from pyglibc._asyncio_abc import AbstractEventLoopPolicy
from pyglibc._asyncio_loop import DefaultEventLoop


__author__ = 'Zygmunt Krynicki <zygmunt.krynicki@canonical.com>'
__all__ = [
    'DefaultEventLoopPolicy',
    'get_event_loop',
    'get_event_loop_policy',
    'new_event_loop',
    'set_event_loop',
    'set_event_loop_policy',
]


class DefaultEventLoopPolicy(AbstractEventLoopPolicy):
    """
    The default event loop policy
    """

    def __init__(self):
        self._event_loop = None

    def get_event_loop(self):
        if self._event_loop is None:
            self._event_loop = self.new_event_loop()
        return self._event_loop

    def set_event_loop(self, event_loop):
        self._event_loop = event_loop

    def new_event_loop(self):
        return DefaultEventLoop()


_current_policy = DefaultEventLoopPolicy()


def get_event_loop():
    """
    Get the event loop associated with the current context.
    """
    return _current_policy.get_event_loop()


def set_event_loop(event_loop):
    """
    Set the event loop associated with the current context.
    """
    return _current_policy.set_event_loop(event_loop)


def new_event_loop():
    """
    Crate a new event loop
    """
    return _current_policy.new_event_loop()


def set_event_loop_policy(policy):
    """
    Set a new event loop policy

    :param policy:
        A AbstractEventLoopPolicy instance or None

    If policy is None then the default policy is restored. Otherwise the new
    policy is replaces the current policy.
    """
    global _current_policy
    if policy is None:
        _current_policy = DefaultEventLoopPolicy()
    else:
        _current_policy = policy


def get_event_loop_policy():
    """
    Get the current event loop policy
    """
    return _current_policy
