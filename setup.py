#!/usr/bin/env python
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
import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


base_dir = os.path.dirname(__file__)
readme = open(os.path.join(base_dir, 'README.rst'), 'rt').read()
history = open(os.path.join(base_dir, 'HISTORY.rst'), 'rt').read()


setup(
    name="glibc",
    version="0.6",
    url="https://github.com/zyga/python-glibc/",
    packages=['pyglibc'],
    py_modules=['glibc'],
    author="Zygmunt Krynicki",
    author_email="zygmunt.krynicki@canonical.com",
    license="LGPLv3",
    platforms=["Linux"],
    description="Pure-Python bindings to glibc (based on ctypes)",
    long_description=readme + '\n\n' + history,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        ('License :: OSI Approved :: '
         'GNU Lesser General Public License v3 (LGPLv3)'),
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    zip_safe=True
)
