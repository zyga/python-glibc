#!/usr/bin/env python
"""
Demo of pythonic pthread_sigmask
"""
from __future__ import print_function
from __future__ import absolute_import

from argparse import ArgumentParser
from signal import SIGINT
from time import sleep

from glibc_pthread_sigmask import pthread_sigmask


def main():
    parser = ArgumentParser()
    parser.add_option(
        '--setmask', action='store_true',
        help='use SIG_SETMASK instead of SIG_BLOCK/SIG_UNBLOCK')
    ns = parser.parse_args()
    print("Initially blocked signals are:", pthread_sigmask.get().signals)
    print("Blocking SIGINT")
    with pthread_sigmask([SIGINT], ns.setmask):
        print("Currently blocked signals are:", pthread_sigmask.get().signals)
        print("Sleeping for 3 seconds...")
        sleep(3)
        print("Done sleeping, unblocking SIGINT")
    print("SIGINT is not blocked anymore")
    print("Finally blocked signals are:", pthread_sigmask.get().signals)
    print("Sleeping for another 3 seconds")
    sleep(3)
    print("Done")


if __name__ == '__main__':
    main()
