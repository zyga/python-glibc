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
from __future__ import print_function

import ctypes
import os
import subprocess
import types

import unittest_ext as unittest
import tempfile_ext as tempfile


class GlibcTests(unittest.TestCase):

    def test_importing_glibc_works(self):
        import glibc
        self.assertIsInstance(glibc, types.ModuleType)

    def test_importing_types_works(self):
        from glibc import sigset_t
        self.assertTrue(issubclass(sigset_t, ctypes.Structure))

    def test_importing_constants_works(self):
        from glibc import SIG_BLOCK
        self.assertIsInstance(SIG_BLOCK, int)

    def test_importing_functions_works(self):
        from glibc import _glibc
        from glibc import signalfd
        self.assertIsInstance(signalfd, _glibc._FuncPtr)

    def test_real_constant_value(self):
        import glibc
        for info in glibc._old._glibc_constants:
            with self.subTest(name=info.name):
                expected = get_real_constant_value(info)
                measured = info.py_value
                # print(info.name, "expected", expected, "measured", measured)
                self.assertEqual(expected, measured)

    def test_real_type_size(self):
        import glibc
        for info in glibc._old._glibc_types:
            with self.subTest(name=info.py_name):
                expected = get_real_type_size(info)
                measured = ctypes.sizeof(getattr(glibc, info.py_name))
                self.assertEqual(expected, measured)

    def test_real_field_offset(self):
        import glibc
        for info in glibc._old._glibc_types:
            for field in info.py_fields:
                with self.subTest(name=info.py_name + '.' + field[0]):
                    expected = get_real_field_offset(info, field[0])
                    measured = getattr(getattr(glibc, info.py_name),
                                       field[0]).offset
                    self.assertEqual(expected, measured)

    def test_real_field_size(self):
        import glibc
        for info in glibc._old._glibc_types:
            for field in info.py_fields:
                with self.subTest(name=info.py_name + '.' + field[0]):
                    expected = get_real_field_size(info, field[0])
                    measured = getattr(getattr(glibc, info.py_name),
                                       field[0]).size
                    self.assertEqual(expected, measured)

    def test_real_alias_size(self):
        # Aliases are just not structs but primitive types that are
        # hidden behind obscure UNIX types for every possible number out
        # there
        import glibc
        for info in glibc._old._glibc_aliases:
            with self.subTest(name=info.py_name):
                expected = get_real_type_size(info)
                measured = ctypes.sizeof(getattr(glibc, info.py_name))
                self.assertEqual(expected, measured)


def get_real_constant_value(info):
    with tempfile.TemporaryDirectory() as tmpdir:
        name_c = os.path.join(tmpdir, 'valueof_{}.c'.format(info.name))
        name_bin = os.path.join(tmpdir, 'valueof_{}.bin'.format(info.name))
        with open(name_c, 'wt') as stream:
            for macro in info.c_macros:
                print(macro, file=stream)
            c_type_name = {
                'i': 'int',
                'I': 'unsigned int',
                'L': 'unsigned long',
            }[info.py_ctype._type_]
            c_printf_format = {
                'i': 'd',
                'I': 'u',
                'L': 'ld',
            }[info.py_ctype._type_]
            print("{} test_const = {};".format(
                c_type_name, info.name), file=stream)
            print("#include <stdio.h>", file=stream)
            print(file=stream)
            print("int main() {", file=stream)
            print(r'  printf("%{}\n", test_const);'.format(c_printf_format),
                  file=stream)
            print("  return 0;", file=stream)
            print("}", file=stream)
        # subprocess.call(['cat', name_c])
        subprocess.check_call([
            'gcc', '-Wall', '-Werror', name_c, '-o', name_bin])
        return int(
            subprocess.check_output([name_bin]).decode("UTF-8").strip())


def get_real_type_size(info):
    with tempfile.TemporaryDirectory() as tmpdir:
        name_c = os.path.join(tmpdir, 'sizeof_{}.c'.format(info.py_name))
        name_bin = os.path.join(tmpdir, 'sizeof_{}.bin'.format(info.py_name))
        with open(name_c, 'wt') as stream:
            for macro in info.c_macros:
                print(macro, file=stream)
            print("#include <stddef.h>", file=stream)
            print("static size_t size = sizeof({});".format(
                info.c_name), file=stream)
            print("#include <stdio.h>", file=stream)
            print(file=stream)
            print("int main() {", file=stream)
            print(r'  printf("%zd\n", size);', file=stream)
            print(r"  return 0;", file=stream)
            print("}", file=stream)
        # subprocess.call(['cat', name_c])
        subprocess.check_call([
            'gcc', '-Wall', '-Werror', name_c, '-o', name_bin])
        return int(
            subprocess.check_output([name_bin]).decode("UTF-8").strip())


def get_real_field_size(info, field):
    with tempfile.TemporaryDirectory() as tmpdir:
        name_c = os.path.join(tmpdir, 'sizeof_{}.{}.c'.format(
            info.py_name, field))
        name_bin = os.path.join(tmpdir, 'sizeof_{}.{}.bin'.format(
            info.py_name, field))
        with open(name_c, 'wt') as stream:
            for macro in info.c_macros:
                print(macro, file=stream)
            print("#include <stddef.h>", file=stream)
            print("static size_t size = sizeof((({} *)0)->{});".format(
                info.c_name, field), file=stream)
            print("#include <stdio.h>", file=stream)
            print(file=stream)
            print("int main() {", file=stream)
            print(r'  printf("%zd\n", size);', file=stream)
            print(r"  return 0;", file=stream)
            print("}", file=stream)
        # subprocess.call(['cat', name_c])
        subprocess.check_call([
            'gcc', '-Wall', '-Werror', name_c, '-o', name_bin])
        return int(
            subprocess.check_output([name_bin]).decode("UTF-8").strip())


def get_real_field_offset(info, field):
    with tempfile.TemporaryDirectory() as tmpdir:
        name_c = os.path.join(tmpdir, 'offsetof_{}.{}.c'.format(
            info.py_name, field))
        name_bin = os.path.join(tmpdir, 'offsetof_{}.{}.bin'.format(
            info.py_name, field))
        with open(name_c, 'wt') as stream:
            for macro in info.c_macros:
                print(macro, file=stream)
            print("#include <stddef.h>", file=stream)
            print("static size_t offset = offsetof({}, {});".format(
                info.c_name, field), file=stream)
            print("#include <stdio.h>", file=stream)
            print(file=stream)
            print("int main() {", file=stream)
            print(r'  printf("%zd\n", offset);', file=stream)
            print(r"  return 0;", file=stream)
            print("}", file=stream)
        # subprocess.call(['cat', name_c])
        subprocess.check_call([
            'gcc', '-Wall', '-Werror', name_c, '-o', name_bin])
        return int(
            subprocess.check_output([name_bin]).decode("UTF-8").strip())


if __name__ == '__main__':
    raise SystemExit(unittest.main())
