"""
epoll(7) + signalfd(2) demo, see the manual page of signalfd(2) and epoll(7)
for the base C-code that inspired this example. NOTE: epoll is used in level
mode (aka, the easy, blocking way)
"""
from __future__ import print_function
from __future__ import absolute_import

from ctypes import byref, cast, POINTER
from os import fdopen, close
from signal import SIGINT, SIGQUIT

from glibc import (
    SIG_BLOCK, SFD_CLOEXEC, EPOLL_CLOEXEC, EPOLLIN, EPOLL_CTL_ADD,
    sigset_t, signalfd_siginfo, epoll_event,
    sigemptyset, sigaddset, sigprocmask, signalfd,
    epoll_create1, epoll_ctl, epoll_wait,
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
    sfd = signalfd(-1, mask, SFD_CLOEXEC)
    # Get a epoll descriptor
    epollfd = epoll_create1(EPOLL_CLOEXEC)
    ev = epoll_event()
    ev.events = EPOLLIN
    ev.data.fd = sfd
    epoll_ctl(epollfd, EPOLL_CTL_ADD, sfd, byref(ev))
    MAX_EVENTS = 10
    events = (epoll_event * MAX_EVENTS)()
    with fdopen(sfd, 'rb', 0) as sfd_stream:
        while True:
            nfds = epoll_wait(
                epollfd, cast(byref(events), POINTER(epoll_event)),
                MAX_EVENTS, -1)
            for event_id in range(nfds):
                if events[event_id].data.fd == sfd:
                    # Read the next delivered signal
                    sfd_stream.readinto(fdsi)
                    if fdsi.ssi_signo == SIGINT:
                        print("Got SIGINT")
                    elif fdsi.ssi_signo == SIGQUIT:
                        print("Got SIGQUIT")
                        return
                    else:
                        print("Read unexpected signal")
                else:
                    raise Exception("unexpected fd?")
    close(sfd)
    close(epollfd)


if __name__ == '__main__':
    main()
