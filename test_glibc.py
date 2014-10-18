# encoding: UTF-8
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
Smoke tests for python-glibc
"""
import ctypes
import types
import unittest


class GlibcTests(unittest.TestCase):

    def test_importing_glibc_works(self):
        import glibc
        self.assertIsInstance(glibc, types.ModuleType)

    def test_importing_types_works(self):
        from glibc import sigset_t
        self.assertTrue(issubclass(sigset_t, ctypes.Structure))

    def test_importing_constants_works(self):
        from glibc import SIG_BLOCK
        self.assertIsInstance(SIG_BLOCK, ctypes.c_int)

    def test_importing_functions_works(self):
        from glibc import _glibc
        from glibc import signalfd
        self.assertIsInstance(signalfd, _glibc._FuncPtr)


if __name__ == '__main__':
    raise SystemExit(unittest.main())
