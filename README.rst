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
* Supports ``dup(2)``, ``dup2(2)``, ``dup3(2)``, ``epoll_create(2)``,
  ``epoll_create1(2)``, ``epoll_ctl(2)``, ``epoll_ctl(2)``, ``epoll_pwait(2)``,
  ``epoll_wait(2)``, ``pipe(2)``, ``pipe2(2)``, ``sigaddset(3)``,
  ``sigdelset(3)``, ``sigemptyset(3)``, ``sigfillset(3)``, ``sigismember(3)``,
  ``signalfd(2)``, ``sigprocmask(2)`` and all the associated data types and
  constants.
* Supported on python 2.7+ and python 3.2+ and pypy
* All other useful glibc features are in scope (patches welcome!)
* ``from glibc import ...`` -- direct access to glibc functions and types via
  lazy imports, fast startup, low memory overhead, efficient calls to glibc
* Declarative code, easy to verify for correctness, easy to add more types,
  functions and constants.
* Translates error codes according to documentation (manual pages) of each
  supported function. Raises OSError with appropriate values and a customized,
  easy-to-understand error message.
