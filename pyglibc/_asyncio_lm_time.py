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
:mod:`pyglibc._asyncio_lm_time` -- Time API
===========================================
"""
from __future__ import absolute_import

from ctypes import byref

from glibc import CLOCK_MONOTONIC
from glibc import clock_gettime
from glibc import timespec

__author__ = 'Zygmunt Krynicki <zygmunt.krynicki@canonical.com>'
__all__ = [
    'lm_time',
]


class lm_time(object):

    def time(self):
        """
        Returns the current time according to the event loop's clock.

        This may be time.time() or time.monotonic() or some other
        system-specific clock, but it must return a float expressing the time
        in units of approximately one second since some epoch.

        No clock is perfect -- see :PEP:`418`.
        """
        t = timespec()
        clock_gettime(CLOCK_MONOTONIC, byref(t))
        return t.tv_sec + t.tv_nsec * 10 ** -9
