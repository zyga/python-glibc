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
:mod:`pyglibc._asyncio_errors` -- Error classes related to asyncio
==================================================================
"""
from __future__ import absolute_import

__author__ = 'Zygmunt Krynicki <zygmunt.krynicki@canonical.com>'
__all__ = [
    'InvalidStateError',
    'InvalidTimeoutError',
    'CancelledError',
    'TimeoutError',
]


class InvalidStateError(Exception):
    """
    Raised whenever the Future is not in a state acceptable to the
    method being called (e.g. calling set_result() on a Future that
    is already done, or calling result() on a Future that is not yet done).
    """


class InvalidTimeoutError(Exception):
    """
    Raised by result() and exception() when a nonzero timeout
    argument is given.
    """


class CancelledError(Exception):
    """
    An alias for concurrent.futures.CancelledError. Raised when result()
    or exception() is called on a Future that is cancelled.
    """


class TimeoutError(Exception):
    """
    An alias for concurrent.futures.TimeoutError.
    May be raised by run_until_complete().
    """
