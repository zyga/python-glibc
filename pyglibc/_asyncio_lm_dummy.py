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
:mod:`pyglibc._asyncio_lm_dummy` -- Dummy event loop modules
============================================================

This module contains dummy implementation of each of the loop module classes
that make up the full PEP3156 event loop class. Each methods on each of the
classes defined here raise ``NotImplementedError``. All those classes are
useful for assembling a "full", API-compliant class easily.
"""
from __future__ import absolute_import

__author__ = 'Zygmunt Krynicki <zygmunt.krynicki@canonical.com>'
__all__ = [
    'lm_dummy_callbacks',
    'lm_dummy_core',
    'lm_dummy_dns',
    'lm_dummy_internet',
    'lm_dummy_io_callbacks',
    'lm_dummy_pipes_subproc',
    'lm_dummy_signal_callbacks',
    'lm_dummy_socket',
    'lm_dummy_threading',
]


class lm_dummy_core(object):

    def run_forever(self):
        raise NotImplementedError()

    def run_until_complete(self, future):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def is_running(self):
        raise NotImplementedError()

    def is_closed(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()


class lm_dummy_callbacks(object):

    def call_soon(self, callback, *args):
        raise NotImplementedError()

    def call_later(self, delay, callback, *args):
        raise NotImplementedError()

    def call_at(self, when, callback, *args):
        raise NotImplementedError()

    def time(self):
        raise NotImplementedError()


class lm_dummy_threading(object):

    def call_soon_threadsafe(self, callback, *args):
        raise NotImplementedError()

    def run_in_executor(self, executor, callback, *args):
        raise NotImplementedError()

    def set_default_executor(self, executor):
        raise NotImplementedError()


class lm_dummy_dns(object):

    def getaddrinfo(self, host, port, family=0, type=0, proto=0, flags=0):
        raise NotImplementedError()

    def getnameinfo(self, sockaddr, flags=0):
        raise NotImplementedError()


class lm_dummy_internet(object):

    def create_connection(self, protocol_factory, host, port, **options):
        raise NotImplementedError()

    def create_server(self, protocol_factory, host, port, **options):
        raise NotImplementedError()

    def create_datagram_endpoint(self, protocol_factory, local_addr=None,
                                 remote_addr=None, **options):
        raise NotImplementedError()


class lm_dummy_socket(object):

    def sock_recv(self, sock, n):
        raise NotImplementedError()

    def sock_sendall(self, sock, data):
        raise NotImplementedError()

    def sock_connect(self, sock, address):
        raise NotImplementedError()

    def sock_accept(self, sock):
        raise NotImplementedError()


class lm_dummy_io_callbacks(object):

    def add_reader(self, fd, callback, *args):
        raise NotImplementedError()

    def add_writer(self, fd, callback, *args):
        raise NotImplementedError()

    def remove_reader(self, fd):
        raise NotImplementedError()

    def remove_writer(self, fd):
        raise NotImplementedError()


class lm_dummy_pipes_subproc(object):

    def connect_read_pipe(self, protocol_factory, pipe):
        raise NotImplementedError()

    def connect_write_pipe(self, protocol_factory, pipe):
        raise NotImplementedError()

    def subprocess_shell(self, protocol_factory, cmd, **options):
        raise NotImplementedError()

    def subprocess_exec(self, protocol_factory, *args, **options):
        raise NotImplementedError()


class lm_dummy_signal_callbacks(object):

    def add_signal_handler(self, sig, callback, *args):
        raise NotImplementedError()

    def remove_signal_handler(self, sig):
        raise NotImplementedError()
