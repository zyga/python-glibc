# Copyright (c) 2014 Canonical Ltd.
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
:mod:`pyglibc._p2k` -- python 2/3 abstractions needed by pyglibc
================================================================

This module is considered a part of the private api of python-glibc. It may
change in the future in an incompatible way.
"""
import abc

__author__ = 'Zygmunt Krynicki <zygmunt.krynicki@canonical.com>'
__version__ = '1.0'
__all__ = ['Interface']


class Interface(metaclass=abc.ABCMeta):
    """
    An empty class with :class:`abc.ABCMeta` metaclass.
    """
