#!/usr/bin/env python
"""
glibc_signalfd demo, this is the high-level version of raw-signalfd-demo
"""
from __future__ import print_function
from __future__ import absolute_import

from signal import SIGINT, SIGQUIT

from pyglibc import signalfd
from pyglibc import pthread_sigmask


def main():
    signals = [SIGINT, SIGQUIT]
    with pthread_sigmask(signals):
        with signalfd(signals) as sfd:
            for fdsi in sfd.read():
                if fdsi.ssi_signo == SIGINT:
                    print("Got SIGINT")
                elif fdsi.ssi_signo == SIGQUIT:
                    print("Got SIGQUIT")
                    return
                else:
                    print("Read unexpected signal")


if __name__ == '__main__':
    main()
