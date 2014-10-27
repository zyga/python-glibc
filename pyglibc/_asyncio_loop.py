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
:mod:`pyglibc._asyncio_loop` -- PEP3156 main loop
=================================================

This module contains the "modular" event loop. Since the full API of the
asyncio event loop is huge I've decided to split it into topic modules. Each
topic is implemented as a separate class (typically in a separate module) and
all the topic classes are combined to form the ModularEventLoop.

Loop modules (``lm_``) that are not interesting in the first stages of the
development of this package are replaced with dummy equivalents.
"""
from __future__ import absolute_import

from pyglibc._asyncio_abc import AbstractEventLoop
from pyglibc._asyncio_lm_core import lm_core
from pyglibc._asyncio_lm_dummy import lm_dummy_callbacks
from pyglibc._asyncio_lm_dummy import lm_dummy_dns
from pyglibc._asyncio_lm_dummy import lm_dummy_internet
from pyglibc._asyncio_lm_dummy import lm_dummy_pipes_subproc
from pyglibc._asyncio_lm_signal_callbacks import lm_signalfd_signal_callbacks
from pyglibc._asyncio_lm_dummy import lm_dummy_socket
from pyglibc._asyncio_lm_dummy import lm_dummy_threading
from pyglibc._asyncio_lm_selector import lm_selector
from pyglibc._asyncio_lm_time import lm_time
from pyglibc._modular import modular_object

__author__ = 'Zygmunt Krynicki <zygmunt.krynicki@canonical.com>'
__all__ = [
    'ModularEventLoop',
    'DefaultEventLoop',
]


class ModularEventLoop(modular_object, AbstractEventLoop):
    """
    Modular, :pep:`3156`-API-compilant event loop
    """
    __modules__ = [
        lm_time,
        lm_dummy_callbacks,
        lm_dummy_threading,
        lm_dummy_dns,
        lm_dummy_internet,
        lm_dummy_socket,
        lm_dummy_pipes_subproc,
        # Set up signal handling next
        lm_signalfd_signal_callbacks,
        # Set up I/O selector next
        lm_selector,
        # Set up core bits first
        lm_core,
    ]


DefaultEventLoop = ModularEventLoop
