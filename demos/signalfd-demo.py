"""
signalfd(2) demo, see the manual page of signalfd(2) for the equivalent C-code
"""
from __future__ import print_function
from __future__ import absolute_import

from signal import SIGINT, SIGQUIT
from os import fdopen

from glibc import (
    SIG_BLOCK,
    sigset_t, signalfd_siginfo,
    sigemptyset, sigaddset, sigprocmask, signalfd,
)


def main():
    # Block signals so that they aren't handled
    # according to their default dispositions
    mask = sigset_t()
    fdsi = signalfd_siginfo()
    sigemptyset(mask)
    sigaddset(mask, SIGINT)
    sigaddset(mask, SIGQUIT)
    sigprocmask(SIG_BLOCK, mask, None)
    # Get a signalfd descriptor
    sfd = signalfd(-1, mask, 0)
    with fdopen(sfd, 'rb', 0) as sfd_stream:
        while True:
            # Read the next delivered signal
            sfd_stream.readinto(fdsi)
            if fdsi.ssi_signo == SIGINT:
                print("Got SIGINT")
            elif fdsi.ssi_signo == SIGQUIT:
                print("Got SIGQUIT")
                return
            else:
                print("Read unexpected signal")


if __name__ == '__main__':
    main()
