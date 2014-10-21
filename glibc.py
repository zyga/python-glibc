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

from ctypes import POINTER
from ctypes import c_int
from ctypes import c_int32
from ctypes import c_uint
from ctypes import c_uint32
from ctypes import c_uint64
from ctypes import c_uint8
from ctypes import c_ulong
from ctypes import c_voidp
from ctypes import get_errno
import collections
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
__version__ = '0.4'


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
        if sys.version_info[0] == 3:
            data = super(LazyModule, self).__dir__()
        else:
            data = self.__dict__.keys()
        data = set(data) | self._all
        return sorted(data)

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


_glibc_typeinfo = collections.namedtuple(
    '_glibc_typeinfo',
    'doc py_kind py_name c_name c_packed py_fields, c_macros')


# Lazily define all supported glibc types
_glibc_types = [
    ("""
     struct sigset_t;
     """,
     'struct', 'sigset_t', 'sigset_t', False, (
         # There's no spec on that, pulled from glibc
         ('__val', c_ulong * (1024 // (8 * ctypes.sizeof(c_ulong)))),
     ), [
         '#include <signal.h>'
     ]),
    ("""
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
     'struct', 'signalfd_siginfo', 'struct signalfd_siginfo', False, (
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
     ), [
         '#include <sys/signalfd.h>'
     ]),
    ("""
     typedef union epoll_data {
         void    *ptr;
         int      fd;
         uint32_t u32;
         uint64_t u64;
     } epoll_data_t;
     """,
     'union', 'epoll_data_t', 'epoll_data_t', False, (
         ('ptr', c_voidp),
         ('fd', c_int),
         ('u32', c_uint32),
         ('u64', c_uint64),
     ), [
         '#include <sys/epoll.h>'
     ]),
    ("""
     struct epoll_event {
         uint32_t     events;    /* Epoll events */
         epoll_data_t data;      /* User data variable */
     };
     """,
     'struct', 'epoll_event', 'struct epoll_event', True, (
         ('events', c_uint32),
         ('data', 'glibc.epoll_data_t'),
     ), [
         '#include <sys/epoll.h>'
     ]),
]


_glibc_types = [_glibc_typeinfo(*i) for i in _glibc_types]


def _glibc_type(doc, py_kind, py_name, c_name, c_packed, py_fields, c_macros):
    _globals = {'ctypes': ctypes, 'glibc': _mod}
    py_fields = tuple([
        (py_field_name, (eval(py_field_type, _globals)
                      if isinstance(py_field_type, str)
                      else py_field_type))
        for py_field_name, py_field_type in py_fields
    ])
    if py_kind == 'struct':
        new_type = type(py_name, (ctypes.Structure, ), {
            '__doc__': doc,
            '_fields_': py_fields,
            '_pack_': c_packed,
        })
    elif py_kind == 'union':
        if c_packed:
            raise ValueError("c_packed is meaningless for unions")
        new_type = type(py_name, (ctypes.Union, ), {
            '__doc__': doc,
            '_fields_': py_fields,
        })
    else:
        raise ValueError("bad value of py_kind")
    return new_type


for info in _glibc_types:
    _mod.lazily(info[2], _glibc_type, info)
del info
# del _glibc_types


_glibc_constantinfo = collections.namedtuple(
    '_glibc_constantinfo', 'name py_ctype py_value c_macros')

# Non-lazily define all supported glibc constants
_glibc_constants = (
    ('SIG_BLOCK',       c_int, 0, ('#include <signal.h>',)),
    ('SIG_UNBLOCK',     c_int, 1, ('#include <signal.h>',)),
    ('SIG_SETMASK',     c_int, 2, ('#include <signal.h>',)),
    ('CLD_EXITED',      c_int, 1, ('#include <signal.h>',)),
    ('CLD_KILLED',      c_int, 2, ('#include <signal.h>',)),
    ('CLD_DUMPED',      c_int, 3, ('#include <signal.h>',)),
    ('CLD_TRAPPED',     c_int, 4, ('#include <signal.h>',)),
    ('CLD_STOPPED',     c_int, 5, ('#include <signal.h>',)),
    ('CLD_CONTINUED',   c_int, 6, ('#include <signal.h>',)),
    ('FD_SETSIZE',      c_int, 1024, ('#include <sys/types.h>',)),
    ('SFD_CLOEXEC',     c_int, 0o2000000, ('#include <sys/signalfd.h>',)),
    ('SFD_NONBLOCK',    c_int, 0o0004000, ('#include <sys/signalfd.h>',)),
    ('EPOLL_CLOEXEC',   c_int, 0o2000000, ('#include <sys/epoll.h>',)),
    # opcodes for epoll_ctl()
    ('EPOLL_CTL_ADD',   c_int, 1, ('#include <sys/epoll.h>',)),
    ('EPOLL_CTL_DEL',   c_int, 2, ('#include <sys/epoll.h>',)),
    ('EPOLL_CTL_MOD',   c_int, 3, ('#include <sys/epoll.h>',)),
    # enum EPOLL_EVENTS
    ('EPOLLIN',         c_uint, 0x0001, ('#include <sys/epoll.h>',)),
    ('EPOLLPRI',        c_uint, 0x0002, ('#include <sys/epoll.h>',)),
    ('EPOLLOUT',        c_uint, 0x0004, ('#include <sys/epoll.h>',)),
    ('EPOLLERR',        c_uint, 0x0008, ('#include <sys/epoll.h>',)),
    ('EPOLLHUP',        c_uint, 0x0010, ('#include <sys/epoll.h>',)),
    ('EPOLLRDNORM',     c_uint, 0x0040, ('#include <sys/epoll.h>',)),
    ('EPOLLRDBAND',     c_uint, 0x0080, ('#include <sys/epoll.h>',)),
    ('EPOLLWRNORM',     c_uint, 0x0100, ('#include <sys/epoll.h>',)),
    ('EPOLLWRBAND',     c_uint, 0x0200, ('#include <sys/epoll.h>',)),
    ('EPOLLMSG',        c_uint, 0x0400, ('#include <sys/epoll.h>',)),
    ('EPOLLRDHUP',      c_uint, 0x2000, ('#include <sys/epoll.h>',)),
    ('EPOLLONESHOT',    c_uint, 1 << 30, ('#include <sys/epoll.h>',)),
    ('EPOLLET',         c_uint, 1 << 31, ('#include <sys/epoll.h>',)),
    # ...
    ('O_CLOEXEC',       c_int, 0o2000000, (
        '#define _POSIX_C_SOURCE 200809L',
        '#include <sys/types.h>',
        '#include <sys/stat.h>',
        '#include <fcntl.h>')),
    ('O_DIRECT',        c_int, 0o0040000, (
        '#define _GNU_SOURCE',
        '#include <sys/types.h>',
        '#include <sys/stat.h>',
        '#include <fcntl.h>')),
    ('O_NONBLOCK',      c_int, 0o00004000, (
        '#define _POSIX_C_SOURCE 200809L',
        '#include <sys/types.h>',
        '#include <sys/stat.h>',
        '#include <fcntl.h>')),
    ('PIPE_BUF',        c_int, 4096, ('#include <limits.h>',)),
)


_glibc_constants = [_glibc_constantinfo(*i) for i in _glibc_constants]


for info in _glibc_constants:
    _mod.immediate(info.name, info.py_value)
del info
# del _glibc_constants


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
    ('epoll_create', c_int, [c_int],
     """int epoll_create(int size);""",
     -1, {
         errno.EINVAL: "size is not positive.",
         errno.EMFILE: ("The per-user limit on the number of epoll instances"
                        " imposed by /proc/sys/fs/epoll/max_user_instances was"
                        " encountered.  See epoll(7) for further details."),
         errno.ENFILE: ("The system limit on the total number of open files"
                        " has been reached."),
         errno.ENOMEM: ("There was insufficient memory to create the kernel"
                        " object."),
     }),
    ('epoll_create1', c_int, [c_int],
     """int epoll_create1(int flags);""",
     -1, {
         errno.EINVAL: "Invalid value specified in flags.",
         errno.EMFILE: ("The per-user limit on the number of epoll instances"
                        " imposed by /proc/sys/fs/epoll/max_user_instances was"
                        " encountered.  See epoll(7) for further details."),
         errno.ENFILE: ("The system limit on the total number of open files"
                        " has been reached."),
         errno.ENOMEM: ("There was insufficient memory to create the kernel"
                        " object."),
     }),
    ('epoll_wait', c_int, [c_int, 'ctypes.POINTER(glibc.epoll_event)', c_int,
                           c_int],
     """int epoll_wait(int epfd, struct epoll_event *events,
                       int maxevents, int timeout);""",
     -1, {
         errno.EBADF: "epfd is not a valid file descriptor.",
         errno.EFAULT: ("The memory area pointed to by events is not"
                        " accessible with write permissions."),
         errno.EINTR: ("The call was interrupted by a signal handler before"
                       " either (1) any of the requested events occurred"
                       " or (2) the timeout expired; see signal(7)."),
         errno.EINVAL: ("epfd is not an epoll file descriptor, or maxevents"
                        " is less than or equal to zero."),
     }),
    ('epoll_pwait', c_int, [c_int, 'ctypes.POINTER(glibc.epoll_event)', c_int,
                            c_int, 'ctypes.POINTER(glibc.sigset_t)'],
     """int epoll_pwait(int epfd, struct epoll_event *events,
                        int maxevents, int timeout,
                        const sigset_t *sigmask);""",
     -1, {
         errno.EBADF: "epfd is not a valid file descriptor.",
         errno.EFAULT: ("The memory area pointed to by events is not"
                        " accessible with write permissions."),
         errno.EINTR: ("The call was interrupted by a signal handler before"
                       " either (1) any of the requested events occurred"
                       " or (2) the timeout expired; see signal(7)."),
         errno.EINVAL: ("epfd is not an epoll file descriptor, or maxevents"
                        " is less than or equal to zero."),
     }),
    ('epoll_ctl', c_int, [c_int, c_int, c_int,
                          'ctypes.POINTER(glibc.epoll_event)'],
     "int epoll_ctl(int epfd, int op, int fd, struct epoll_event *event);",
     -1, {
         errno.EBADF: "epfd or fd is not a valid file descriptor.",
         errno.EEXIST: ("op was EPOLL_CTL_ADD, and the supplied file"
                        " descriptor fd is already registered with this"
                        " epoll instance."),
         errno.EINVAL: ("epfd is not an epoll file descriptor, or fd is the"
                        " same as epfd, or the requested operation op is not"
                        " supported by this interface."),
         errno.ENOENT: ("op was EPOLL_CTL_MOD or EPOLL_CTL_DEL, and fd is not"
                        " registered with this epoll instance."),
         errno.ENOMEM: ("There was insufficient memory to handle the requested"
                        " op control operation."),
         errno.ENOSPC: ("The limit imposed by"
                        " /proc/sys/fs/epoll/max_user_watches was encountered"
                        " while trying to register (EPOLL_CTL_ADD) a new file"
                        " descriptor on an epoll instance. See epoll(7) for"
                        " further details."),
         errno.EPERM: "The target file fd does not support epoll.",
     }),
    ('pipe', c_int, [POINTER(c_int * 2)],
     """int pipe2(int pipefd[2], int flags);""",
     -1, {
         errno.EFAULT: "pipefd is not valid.",
         errno.EMFILE: "Too many file descriptors are in use by the process.",
         errno.ENFILE: ("The system limit on the total number of open files"
                        " has been reached."),
     }),
    ('pipe2', c_int, [POINTER(c_int * 2), c_int],
     """int pipe2(int pipefd[2], int flags);""",
     -1, {
         errno.EFAULT: "pipefd is not valid.",
         errno.EINVAL: "Invalid value in flags.",
         errno.EMFILE: "Too many file descriptors are in use by the process.",
         errno.ENFILE: ("The system limit on the total number of open files"
                        " has been reached."),
     }),
    ('dup', c_int, [c_int],
     """int dup(int oldfd);""",
     -1, {
         errno.EBADF: ("oldfd isn't an open file descriptor, or newfd is out"
                       " of the allowed range for file descriptors."),
         errno.EMFILE: ("The process already has the maximum number of file"
                        " descriptors open and tried to open a new one."),
     }),
    ('dup2', c_int, [c_int, c_int],
     """int dup2(int oldfd, int newfd);""",
     -1, {
         errno.EBADF: ("oldfd isn't an open file descriptor, or newfd is out"
                       " of the allowed range for file descriptors."),
         errno.EBUSY: ("(Linux only) This may be returned by dup2() or dup3()"
                       " during a race condition with open(2) and dup()."),
         errno.EINTR: ("The dup2() or dup3() call was interrupted by a signal;"
                       " see signal(7)."),
         errno.EMFILE: ("The process already has the maximum number of file"
                        " descriptors open and tried to open a new one."),
     }),
    ('dup3', c_int, [c_int, c_int, c_int],
     """int dup3(int oldfd, int newfd, int flags);""",
     -1, {
         errno.EBADF: ("oldfd isn't an open file descriptor, or newfd is out"
                       " of the allowed range for file descriptors."),
         errno.EBUSY: ("(Linux only) This may be returned by dup2() or dup3()"
                       " during a race condition with open(2) and dup()."),
         errno.EINTR: ("The dup2() or dup3() call was interrupted by a signal;"
                       " see signal(7)."),
         errno.EINVAL: ("(dup3()) flags contain an invalid value.  Or, oldfd"
                        " was equal to newfd."),
         errno.EMFILE: ("The process already has the maximum number of file"
                        " descriptors open and tried to open a new one."),
     }),
    ('close', c_int, [c_int],
     """int close(int fd);""",
     -1, {
         errno.EBADF: "fd isn't a valid open file descriptor.",
         errno.EINTR: ("The close() call was interrupted by a signal;"
                       " see signal(7)."),
         errno.EIO: "An I/O error occurred."
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
