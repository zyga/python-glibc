#!/usr/bin/env python
"""
glibc_signalfd demo, this is the high-level version of raw-signalfd-demo
"""
from __future__ import print_function
from __future__ import absolute_import

import signal

from glibc import pause


def on_SIGINT(signal, frame):
    return


def main():
    signal.signal(signal.SIGINT, on_SIGINT)
    print("Pausing (interrupt to continue)")
    pause()

if __name__ == '__main__':
    main()
