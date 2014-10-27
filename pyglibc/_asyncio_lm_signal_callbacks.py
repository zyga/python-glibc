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
:mod:`pyglibc._asyncio_lm_signal_callbacks -- Signal callbacks
==============================================================
"""
from __future__ import absolute_import

import collections
import logging
import signal

from glibc import SFD_CLOEXEC
from glibc import SFD_NONBLOCK
from pyglibc import pthread_sigmask
from pyglibc import signalfd
from pyglibc._modular import multiplexed

__author__ = 'Zygmunt Krynicki <zygmunt.krynicki@canonical.com>'
__all__ = [
    'lm_signalfd_signal_callbacks',
]

_logger = logging.getLogger('asyncio')


signal_handler = collections.namedtuple(
    "signal_handler", "signal callback args")


class lm_signalfd_signal_callbacks(object):

    @multiplexed
    def __init__(self, **kwargs):
        _logger.debug("Setting up signal handling")
        self.__handlers = {}  # signal number -> signal_callback_info
        self.__sigmask = pthread_sigmask()
        # XXX: does asyncio handle signals when the loop is off or just when
        # running? I bet it's instant but let's check that later.
        self.__sigmask.block()
        _logger.debug("Set up pthread_sigmask(2)")
        self.__signalfd = signalfd(flags=SFD_CLOEXEC | SFD_NONBLOCK)
        _logger.debug("Set up signalgfd(2)")
        self.add_reader(self.__signalfd.fileno(), self.__read_pending_signals)
        _logger.debug("Added internal reader for signalfd() data")

    @multiplexed(inversed=True)
    def close(self):
        _logger.debug("Shutting down signal handling")
        self.remove_reader(self.__signalfd.fileno())
        _logger.debug("Removed internal reader for signalfd() data")
        self.__signalfd.close()
        _logger.debug("Closed signalfd(2)")
        self.__sigmask.unblock()
        _logger.debug("Unblocked signals blocked with pthread_sigmask(2)")
        self.__handlers.clear()

    def add_signal_handler(self, sig, callback, *args):
        # Some signals cannot be handled so let's bail early
        if sig in (signal.SIGKILL, signal.SIGSTOP):
            raise ValueError("this signal cannot be handled")
        if sig not in self.__handlers:
            signals = set(self.__handlers)
            signals.add(sig)
            # XXX: is this order of updates correct?
            self.__sigmask.signals = signals
            self.__signalfd.signals = signals
            _logger.debug("Added blocking+watching for signal %d", sig)
        self.__handlers[sig] = signal_handler(sig, callback, args)

    def remove_signal_handler(self, sig):
        if sig not in self.__handlers:
            return False
        signals = set(self.__handlers)
        signals.remove(sig)
        # XXX: is this order of updates correct?
        self.__sigmask.signals = signals
        self.__signalfd.signals = signals
        del self.__handlers[sig]
        _logger.debug("Removed blocking+watching for signal %d", sig)
        return True

    def __read_pending_signals(self):
        _logger.debug("Reading singals from signalfd...")
        try:
            fdsi_list = self.__signalfd.read()
        except OSError as exc:
            _logger.error("Cannot read pending signals: %r", exc)
            return
        else:
            _logger.debug("Found pending signals: %d", len(fdsi_list))
        for fdsi in fdsi_list:
            self.__process_signal(fdsi)

    def __process_signal(self, fdsi):
        signo = fdsi.ssi_signo
        try:
            handler = self.__handlers[signo]
        except KeyError:
            _logger.error(
                "Received signal %d but there's no handler?", signo)
        else:
            _logger.debug("Dispatching reaction to signal %d", signo)
            _logger.debug("Handler callback: %r", handler.callback)
            _logger.debug("Handler arguments: %r", handler.args)
            # TODO: add a way to get non-standard, extended information that we
            # collected in signo and pass that down to the handler via a
            # keyword argument of some sort?
            handler.callback(*handler.args)
