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
glibc -- things from glibc that have no python interface
========================================================

This package contains ``ctypes`` based wrappers around several missing
functions from glibc. Only missing objects are provided though. Please get the
rest from python's stdlib (aka ``signal``, ``posix`` and ``os``).

.. note::
    If you found that a glibc function that you'd like to use, is missing,
    please open a bug or provide a patch (it's trivial, just look at existing
    functions as an example). All glibc functions are in scope.
"""
from __future__ import absolute_import
from __future__ import division

from ctypes import c_int
from ctypes import c_int32
from ctypes import c_uint32
from ctypes import c_uint64
from ctypes import c_uint8
from ctypes import c_ulong
from ctypes import get_errno
import ctypes
import ctypes.util
import errno
import inspect
import os
import sys
import types

__all__ = [
    # NOTE: __all__ in this module is magic!
    # This value is extended with types, constants and function from glibc
]
__author__ = 'Zygmunt Krynicki <zygmunt.krynicki@canonical.com>'
__version__ = '0.1'


# Load the standard C library on this system
_glibc = ctypes.CDLL(ctypes.util.find_library('c'), use_errno=True)


class LazyModule(types.ModuleType):
    """
    A module subclass that imports things lazily on demand.

    There are some special provisions to make dir() and __all__ work better so
    that pydoc is more informative.

    :ivar _lazy:
        A mapping of 'name' to 'callable'. The callable is called only once and
        defines the lazily loaded version of 'name'.
    :ivar _all:
        A set of all the "public" objects. This is exposed as the module's
        __all__ property. It automatically collects all the objects reported
        via :meth:`lazily()` and :meth:`immediate()`.
    :ivar _old:
        Reference to the old (original) module. This is kept around for python
        2.x compatibility. It also seems to help with implementing __dir__()
    """

    def __init__(self, name, doc, old):
        super(LazyModule, self).__init__(name, doc)
        self._lazy = {}
        self._all = set()
        self._old = old

    def __dir__(self):
        """
        Lazy-aware version of __dir__()
        """
        data = object.__dir__(self)
        data.extend(self._all)
        return data

    def __getattr__(self, name):
        """
        Lazy-aware version of __getattr__()
        """
        try:
            callable, args = self._lazy[name]
        except KeyError:
            raise AttributeError(name)
        value = callable(*args)
        del self._lazy[name]
        setattr(self, name, value)
        return value

    @classmethod
    def shadow_normal_module(cls, mod_name=None):
        """
        Shadow a module with an instance of LazyModule

        :param mod_name:
            Name of the module to shadow. By default this is the module that is
            making the call into this method. This is not hard-coded as that
            module might be called '__main__' if it is executed via 'python -m'
        :returns:
            A fresh instance of :class:`LazyModule`.
        """
        if mod_name is None:
            frame = inspect.currentframe()
            try:
                mod_name = frame.f_back.f_locals['__name__']
            finally:
                del frame
        orig_mod = sys.modules[mod_name]
        lazy_mod = cls(orig_mod.__name__, orig_mod.__doc__, orig_mod)
        for attr in dir(orig_mod):
            setattr(lazy_mod, attr, getattr(orig_mod, attr))
        sys.modules[mod_name] = lazy_mod
        return lazy_mod

    def lazily(self, name, callable, args):
        """
        Load something lazily
        """
        self._lazy[name] = callable, args
        self._all.add(name)

    def immediate(self, name, value):
        """
        Load something immediately
        """
        setattr(self, name, value)
        self._all.add(name)

    @property
    def __all__(self):
        """
        A lazy-aware version of __all__

        In addition to exposing all of the original module's __all__ it also
        contains all the (perhaps not yet loaded) objects defined via
        :meth:`lazily()`
        """
        return sorted(self._all)

    @__all__.setter
    def __all__(self, value):
        """
        Setter for __all__ that just updates the internal set :ivar:`_all`

        This is used by :meth:`shadow_normal_module()` which copies (assigns)
        all of the original module's attributes, which also assigns __all__.
        """
        self._all.update(value)


# Replace 'glibc' module in sys.modules with LazyModule
_mod = LazyModule.shadow_normal_module()


# Lazily define all supported glibc types
_glibc_types = ((
    """
    struct sigset_t;
    """,
    'struct', 'sigset_t', 128, (
        # There's no spec on that, pulled from glibc
        ('__val', c_ulong * (1024 // (8 * ctypes.sizeof(c_ulong)))),
    )
), ("""
    struct signalfd_siginfo {
        uint32_t ssi_signo;   /* Signal number */
        int32_t  ssi_errno;   /* Error number (unused) */
        int32_t  ssi_code;    /* Signal code */
        uint32_t ssi_pid;     /* PID of sender */
        uint32_t ssi_uid;     /* Real UID of sender */
        int32_t  ssi_fd;      /* File descriptor (SIGIO) */
        uint32_t ssi_tid;     /* Kernel timer ID (POSIX timers)
        uint32_t ssi_band;    /* Band event (SIGIO) */
        uint32_t ssi_overrun; /* POSIX timer overrun count */
        uint32_t ssi_trapno;  /* Trap number that caused signal */
        int32_t  ssi_status;  /* Exit status or signal (SIGCHLD) */
        int32_t  ssi_int;     /* Integer sent by sigqueue(3) */
        uint64_t ssi_ptr;     /* Pointer sent by sigqueue(3) */
        uint64_t ssi_utime;   /* User CPU time consumed (SIGCHLD) */
        uint64_t ssi_stime;   /* System CPU time consumed (SIGCHLD) */
        uint64_t ssi_addr;    /* Address that generated signal
                                 (for hardware-generated signals) */
        uint8_t  pad[X];      /* Pad size to 128 bytes (allow for
                                 additional fields in the future) */
    };""",
    'struct', 'signalfd_siginfo', 128, (
        ('ssi_signo', c_uint32),
        ('ssi_errno', c_int32),
        ('ssi_code', c_int32),
        ('ssi_pid', c_uint32),
        ('ssi_uid', c_uint32),
        ('ssi_fd', c_int32),
        ('ssi_tid', c_uint32),
        ('ssi_band', c_uint32),
        ('ssi_overrun', c_uint32),
        ('ssi_trapno', c_uint32),
        ('ssi_status', c_int32),
        ('ssi_int', c_int32),
        ('ssi_ptr', c_uint64),
        ('ssi_utime', c_uint64),
        ('ssi_stime', c_uint64),
        ('ssi_addr', c_uint64),
        ('pad', c_uint8 * 44),
    )))


def _glibc_type(doc, kind, name, size, fields):
    if kind == 'struct':
        new_type = type(name, (ctypes.Structure, ), {
            '__doc__': doc,
            '_fields_': fields,
        })
    else:
        raise ValueError(kind)
    assert ctypes.sizeof(new_type) == size, \
        "{} {} size mismatch".format(kind, name)
    return new_type


for info in _glibc_types:
    _mod.lazily(info[2], _glibc_type, info)
del info
del _glibc_types


# Lazily define all supported glibc constants
_glibc_constants = (
    ('SIG_BLOCK', c_int(0)),
    ('SFD_CLOEXEC', c_int(0o2000000)),
    ('SFD_NONBLOCK', c_int(0o0004000)),
)


for info in _glibc_constants:
    _mod.immediate(info[0], info[1])
del info
del _glibc_constants


# Lazily define all supported glibc functions
_glibc_functions = (
    ('sigemptyset', c_int, ['ctypes.POINTER(glibc.sigset_t)'],
     """int sigemptyset(sigset_t *set);""",
     -1, {
         errno.EINVAL: "sig is not a valid signal"
     }),
    ('sigfillset', c_int, ['ctypes.POINTER(glibc.sigset_t)'],
     """int sigfillset(sigset_t *set);""",
     -1, {
         errno.EINVAL: "sig is not a valid signal"
     }),
    ('sigaddset', c_int, ['ctypes.POINTER(glibc.sigset_t)', c_int],
     """int sigaddset(sigset_t *set, int signum);""",
     -1, {
         errno.EINVAL: "sig is not a valid signal"
     }),
    ('sigdelset', c_int, ['ctypes.POINTER(glibc.sigset_t)', c_int],
     """int sigdelset(sigset_t *set, int signum);""",
     -1, {
         errno.EINVAL: "sig is not a valid signal"
     }),
    ('sigismember', c_int, ['ctypes.POINTER(glibc.sigset_t)', c_int],
     """int sigismember(sigset_t *set, int signum);""",
     -1, {
         errno.EINVAL: "sig is not a valid signal"
     }),
    ('sigprocmask', c_int, [c_int, 'ctypes.POINTER(glibc.sigset_t)',
                            'ctypes.POINTER(glibc.sigset_t)'],
     """int sigprocmask(int how, const sigset_t *set, sigset_t *oldset);""",
     -1, {
         errno.EFAULT: ("The ``set`` or ``oldset`` arguments points outside"
                        " of the process's address space"),
         errno.EINVAL: "The value specified in ``how`` was invalid",
     }),
    ('signalfd', c_int, [c_int, 'ctypes.POINTER(glibc.sigset_t)', c_int],
     """int signalfd(int fd, const sigset_t *mask, int flags);""",
     -1, {
         errno.EBADF: "The fd file descriptor is not a valid file descriptor",
         errno.EINVAL: ("fd is not a valid signalfd file descriptor; "
                        "flags is invalid; "
                        "in Linux 2.6.26 or earlier, flags is nonzero"),
         errno.EMFILE: ("The per-process limit of open file descriptors has"
                        " been reached"),
         errno.ENFILE: ("The system-wide limit on the total number of open",
                        " file descriptors has been reached"),
         errno.ENODEV: ("Could not mount (internal) anonymous inode device"),
         errno.ENOMEM: ("There was insufficient memory to create a new"
                        " signalfd file descriptor")
     }),
)


def _glibc_func(name, restype, argtypes, doc,
                error_result=None, errno_map=None):
    func = getattr(_glibc, name)
    _globals = {'ctypes': ctypes, 'glibc': _mod}
    func.argtypes = [
        eval(argtype, _globals) if isinstance(argtype, str) else argtype
        for argtype in argtypes
    ]
    func.restype = (
        eval(restype, _globals) if isinstance(restype, str) else restype)
    if errno_map is not None:
        # Use built-in error-code to errno translator
        def std_errcheck(result, func, arguments):
            if result == error_result:
                errno = get_errno()
                raise OSError(errno, errno_map.get(errno, os.strerror(errno)))
            return result
        func.errcheck = std_errcheck
    return func


for info in _glibc_functions:
    _mod.lazily(info[0], _glibc_func, info)
del info
del _glibc_functions
