===============================================
Pure-Python bindings to glibc (based on ctypes)
===============================================

.. image:: https://badge.fury.io/py/glibc.png
    :target: http://badge.fury.io/py/glibc

.. image:: https://travis-ci.org/zyga/python-glibc.png?branch=master
        :target: https://travis-ci.org/zyga/python-glibc

.. image:: https://pypip.in/d/glibc/badge.png
        :target: https://pypi.python.org/pypi/glibc

Features
========

* Free software: LGPLv3 license
* Works on python 2.7+ and python 3.2+ and pypy
* Currently exposes 23 low-level glibc functions (see below), 10 data types and
  118 constants. All useful glibc features are in scope (patches welcome!)
* ``from glibc import ...`` -- direct access to glibc constants, functions and
  types via lazy imports, fast startup, low memory overhead, efficient calls to
  glibc
* Translates error codes according to documentation (manual pages) of each
  supported function. Raises OSError with appropriate values and a customized,
  easy-to-understand error message.
* Uses declarative "bindings", easy to verify for correctness, easy to add more
  types, functions and constants. Built-in tests verify the value of each
  constant, size and offset of each structure / union field and the size of the
  whole structure / union.
* Adds high-level abstractions on top of raw functions (pyglibc.select,
  pyglibc.signalfd, pyglibc.selectors, pyglibc.pthread_sigmask) so that using
  them is easier and more pythonic.
* This code is entirely optional and users can still call the low-level
  C-equivalents directly.
* Where possible, existing Python APIs are followed so that glibc_select and
  glibc_selectors are drop-in replacements for the select and selectors modules
  from Python's standard library.

Functions
=========

The following glibc functions are supported

===========================  =================================
           Name                           Remarks
===========================  =================================
``close(2)``                 Same as os.close()
``dup(2)``                   Same as os.dup()
``dup2(2)``                  Same as os.dup2()
``dup3(2)``                  Same as os.dup(flags=)
``epoll_create(2)``          Similar to select.epoll()
``epoll_create1(2)``         Similar to select.epoll()
``epoll_ctl(2)``             Similar to select.epoll.{register,unregister,modify}
``epoll_pwait(2)``
``epoll_wait(2)``            Similar to select.epoll.poll()
``pause(2)``
``pipe(2)``                  Same as os.pipe
``pipe2(2)``
``prctl(2)``
``pthread_sigmask(2)``
``read(2)``                  Unlike os.read, this one makes no copies
``sigaddset(3)``
``sigdelset(3)``
``sigemptyset(3)``
``sigfillset(3)``
``sigismember(3)``
``signalfd(2)``
``sigprocmask(2)``
``timerfd_create(2)``
``timerfd_gettime(2)``
``timerfd_settime(2)``
