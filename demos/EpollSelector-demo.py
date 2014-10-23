#!/usr/bin/env python
"""
EpollSelector +  signalfd(2) demo, see the manual page of signalfd(2) and
epoll(7) for the base C-code that inspired this example. NOTE: epoll is used in
level mode
"""
from __future__ import print_function
from __future__ import absolute_import

from os import (close, fork, execlp, read, waitid, WEXITSTATUS,
                WIFSIGNALED, WCOREDUMP, WNOHANG, WCONTINUED, WEXITED, WSTOPPED,
                WUNTRACED, P_PID)
from signal import SIGINT, SIGQUIT, SIGCHLD, SIGPIPE
from sys import argv

from glibc import (
    SFD_CLOEXEC, SFD_NONBLOCK, O_CLOEXEC, O_NONBLOCK, PIPE_BUF, CLD_EXITED,
    CLD_KILLED, CLD_DUMPED, CLD_STOPPED, CLD_TRAPPED, CLD_CONTINUED, dup3,
)

from contextlib import ExitStack

from pyglibc import pipe2
from pyglibc import signalfd
from pyglibc import pthread_sigmask
from pyglibc.selectors import EpollSelector, EVENT_READ


def main():
    with ExitStack() as stack:
        # Block signals so that they aren't handled according to their default
        # dispositions until after this block is terminated, or, in our case,
        # never since we also use signalfd to collect them.
        print("Blocking signals...")
        stack.enter_context(pthread_sigmask([SIGCHLD]))
        print("Setting up epoll...")
        es = EpollSelector()
        print("Got", es)
        print("Setting up signalfd...")
        sfd_obj = stack.enter_context(
            signalfd([SIGCHLD], SFD_CLOEXEC | SFD_NONBLOCK))
        print("Got", sfd_obj)
        print("Adding signalfd epoll...")
        es.register(sfd_obj, EVENT_READ, 'signalfd(2)')
        print("Setting up stdout pipe...")
        stdout_pair = pipe2(O_CLOEXEC | O_NONBLOCK)
        print("Got", stdout_pair)
        print("Adding stdout pipe to epoll...")
        es.register(stdout_pair[0], EVENT_READ, 'stdout')
        print("Getting stderr pipe...")
        stderr_pair = pipe2(O_CLOEXEC | O_NONBLOCK)
        print("Got", stderr_pair)
        print("Adding stderr pipe to epoll...")
        es.register(stderr_pair[0], EVENT_READ, 'stderr')
        prog = argv[1:]
        if not prog:
            prog = ['echo', 'usage: demo.py PROG [ARGS]']
        print("Going to start program:", prog)
        # Fork :-)
        pid = fork()
        if pid == 0:  # Child.
            # NOTE: we are not closing any of the pipe ends. Why? Because they
            # are all O_CLOEXEC and will thus not live across the execlp call
            # down below.
            dup3(stdout_pair[1], 1, 0)
            dup3(stderr_pair[1], 2, 0)
            execlp(prog[0], *prog)
            return -1
        else:
            close(stdout_pair[1])
            close(stderr_pair[1])
        waiting_for = set(['stdout', 'stderr', 'proc'])
        while waiting_for:
            print("Waiting for events...", ' '.join(waiting_for), flush=True)
            event_list = es.select()
            print("EpollSelector.select() read {} events".format(
                len(event_list)))
            for key, events in event_list:
                print("[event]")
                print(" key: {!r}".format(key))
                print(" events: {!r}".format(events))
                if key.fd == sfd_obj.fileno():
                    print("signalfd() descriptor ready")
                    if events & EVENT_READ:
                        print("Reading data from signalfd()...")
                        # Read the next delivered signal
                        try:
                            fdsi = sfd_obj.read()[0]
                        except IndexError:
                            continue
                        if fdsi.ssi_signo == SIGINT:
                            print("Got SIGINT")
                        elif fdsi.ssi_signo == SIGQUIT:
                            print("Got SIGQUIT")
                            raise SystemExit("exiting prematurly")
                        elif fdsi.ssi_signo == SIGCHLD:
                            print("Got SIGCHLD")
                            waitid_result = waitid(
                                P_PID, pid,
                                WNOHANG |
                                WEXITED | WSTOPPED | WCONTINUED |
                                WUNTRACED)
                            if waitid_result is None:
                                print("child not ready")
                            else:
                                print("child event")
                                print("si_pid:", waitid_result.si_pid)
                                print("si_uid:", waitid_result.si_uid)
                                print("si_signo:", waitid_result.si_signo)
                                assert waitid_result.si_signo == SIGCHLD
                                print("si_status:", waitid_result.si_status)
                                print("si_code:", waitid_result.si_code)
                                if waitid_result.si_code == CLD_EXITED:
                                    # assert WIFEXITED(waitid_result.si_status)
                                    print("child exited normally")
                                    print("exit code:",
                                          WEXITSTATUS(waitid_result.si_status))
                                    waiting_for.remove('proc')
                                    if 'stdout' in waiting_for:
                                        es.unregister(stdout_pair[0])
                                        close(stdout_pair[0])
                                        waiting_for.remove('stdout')
                                    if 'stderr' in waiting_for:
                                        es.unregister(stderr_pair[0])
                                        close(stderr_pair[0])
                                        waiting_for.remove('stderr')
                                elif waitid_result.si_code == CLD_KILLED:
                                    assert WIFSIGNALED(waitid_result.si_status)
                                    print("child was killed by signal")
                                    print("death signal:",
                                          waitid_result.si_status)
                                    waiting_for.remove('proc')
                                elif waitid_result.si_code == CLD_DUMPED:
                                    assert WIFSIGNALED(waitid_result.si_status)
                                    print("core:",
                                          WCOREDUMP(waitid_result.si_status))
                                elif waitid_result.si_code == CLD_STOPPED:
                                    print("child was stopped")
                                    print("stop signal:",
                                          waitid_result.si_status)
                                elif waitid_result.si_code == CLD_TRAPPED:
                                    print("child was trapped")
                                    # TODO: we could explore trap stuff here
                                elif waitid_result.si_code == CLD_CONTINUED:
                                    print("child was continued")
                                else:
                                    raise SystemExit(
                                        "Unknown CLD_ code: {}".format(
                                            waitid_result.si_code))
                        elif fdsi.ssi_signo == SIGPIPE:
                            print("Got SIGPIPE")
                        else:
                            print("Read unexpected signal: {}".format(
                                fdsi.ssi_signo))
                elif key.fd in (stdout_pair[0], stderr_pair[0]):
                    print("{} pipe() descriptor ready".format(key.data))
                    if events & EVENT_READ:
                        print("Reading data from {} pipe...".format(key.data))
                        data = read(key.fd, PIPE_BUF)
                        print("Read {} bytes from {} pipe".format(
                            len(data), key.data))
                        print("Data:", data)
                        if len(data) == 0:
                            print("Removing {} pipe from EpollSelector".format(
                                key.data))
                            es.unregister(key.fd)
                            print("Closing pipe")
                            close(key.fd)
                            waiting_for.remove(key.data)
                else:
                    # FIXME: we are still getting weird activation events on fd
                    # 0 (stdin) with events == 0 (nothing). I cannot explain
                    # this yet.
                    print("Unexpected descriptor ready:", key.fd)
    assert not waiting_for


if __name__ == '__main__':
    main()
