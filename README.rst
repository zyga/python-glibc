===============================================
Pure-Python bindings to glibc (based on ctypes)
===============================================

.. image:: https://badge.fury.io/py/python-glibc.png
    :target: http://badge.fury.io/py/python-glibc

.. image:: https://travis-ci.org/zyga/python-glibc.png?branch=master
        :target: https://travis-ci.org/zyga/python-glibc

.. image:: https://pypip.in/d/python-glibc/badge.png
        :target: https://pypi.python.org/pypi/python-glibc

Features
========

* Free software: LGPLv3 license
* Supports ``signalfd(2)`` and the assorted set of signal related functions.
* Supported on python 2.7+ and python 3.2+ and pypy
* All other useful glibc features are in scope (patches welcome!)
* ``from glibc import ...`` -- direct access to glibc functions and types via
  lazy imports, fast startup, low memory overhead, efficient calls to glibc
* Declarative code, easy to verify for correctness, easy to add more types,
  functions and constants.
* Translates error codes according to documentation (manual pages) of each
  supported function. Raises OSError with appropriate values and a customized,
  easy-to-understand error message.
