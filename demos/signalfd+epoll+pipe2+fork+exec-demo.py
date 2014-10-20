"""
epoll(7) + signalfd(2) demo, see the manual page of signalfd(2) and epoll(7)
for the base C-code that inspired this example. NOTE: epoll is used in level
mode (aka, the easy, blocking way)
"""
from __future__ import print_function
from __future__ import absolute_import

from ctypes import c_int, c_uint32, byref, cast, POINTER
from os import (fdopen, close, fork, execlp, read, waitid, WIFEXITED,
                WEXITSTATUS, WIFSIGNALED, WCOREDUMP, WNOHANG, WCONTINUED,
                WEXITED, WSTOPPED, WUNTRACED, P_PID)
from signal import SIGINT, SIGQUIT, SIGCHLD, SIGPIPE
from sys import argv

from glibc import (
    SIG_BLOCK, SIG_UNBLOCK,
    SFD_CLOEXEC,
    O_CLOEXEC,
    EPOLL_CLOEXEC,
    EPOLLIN, EPOLLOUT, EPOLLRDHUP, EPOLLPRI, EPOLLERR, EPOLLHUP,
    EPOLL_CTL_ADD, EPOLL_CTL_DEL,
    PIPE_BUF,
    CLD_EXITED, CLD_KILLED, CLD_DUMPED, CLD_STOPPED, CLD_TRAPPED,
    CLD_CONTINUED,
    sigset_t, signalfd_siginfo, epoll_event, sigemptyset, sigaddset,
    sigprocmask, signalfd, epoll_create1, epoll_ctl, epoll_wait, pipe2, dup3,
)


def main():
    # Block signals so that they aren't handled
    # according to their default dispositions
    mask = sigset_t()
    fdsi = signalfd_siginfo()
    sigemptyset(mask)
    sigaddset(mask, SIGINT)
    sigaddset(mask, SIGQUIT)
    sigaddset(mask, SIGCHLD)
    sigaddset(mask, SIGPIPE)
    print("Blocking signals")
    sigprocmask(SIG_BLOCK, mask, None)
    # Get a signalfd descriptor
    sfd = signalfd(-1, mask, SFD_CLOEXEC)
    print("Got signalfd", sfd)
    # Get a epoll descriptor
    epollfd = epoll_create1(EPOLL_CLOEXEC)
    print("Got epollfd", epollfd)
    ev = epoll_event()
    ev.events = EPOLLIN
    ev.data.fd = sfd
    print("Adding signalfd fd {} to epoll".format(sfd))
    epoll_ctl(epollfd, EPOLL_CTL_ADD, sfd, byref(ev))
    # Get two pair of pipes, one for stdout and one for stderr
    stdout_pair = (c_int * 2)()
    pipe2(byref(stdout_pair), O_CLOEXEC)
    print("Got stdout pipe pair", stdout_pair[0], stdout_pair[1])
    stderr_pair = (c_int * 2)()
    pipe2(byref(stderr_pair), O_CLOEXEC)
    print("Got stderr pipe pair", stderr_pair[0], stderr_pair[1])
    prog = argv[1:]
    if not prog:
        prog = ['echo', 'usage: demo.py PROG [ARGS]']
    print("Going to start program:", prog)
    # Fork :-)
    pid = fork()
    if pid == 0:  # Child.
        # NOTE: we are not closing any of the pipe ends. Why? Because they are
        # all O_CLOEXEC and will thus not live across the execlp call down
        # below.
        dup3(stdout_pair[1], 1, 0)
        dup3(stderr_pair[1], 2, 0)
        execlp(prog[0], *prog)
    else:
        for pair in stdout_pair, stderr_pair:
            read_end, write_end = pair
            # We need to close the write sides of both pipes
            close(write_end)
            # And add the read side to epoll
            ev.events = c_uint32(EPOLLIN | EPOLLHUP |
                                 EPOLLERR | EPOLLRDHUP |
                                 EPOLLOUT | EPOLLPRI)
            ev.data.fd = read_end
            print("Adding pipe fd {} to epoll".format(read_end))
            epoll_ctl(epollfd, EPOLL_CTL_ADD, read_end, byref(ev))
        stdout_pipe_fd = stdout_pair[0]
        stderr_pipe_fd = stderr_pair[0]
    with fdopen(sfd, 'rb', 0) as sfd_stream:
        MAX_EVENTS = 10
        event_array = (epoll_event * MAX_EVENTS)()
        waiting_for = set(['stdout', 'stderr', 'proc'])
        while waiting_for:
            print("Waiting for events...", waiting_for, flush=True)
            nfds = epoll_wait(epollfd, cast(
                byref(event_array), POINTER(epoll_event)
            ), MAX_EVENTS, -1)
            print("epoll_wait() read {} events".format(nfds))
            for event_id in range(nfds):
                event = event_array[event_id]
                print("[event {}]".format(event_id))
                event_bits = []
                if event.events & EPOLLIN == EPOLLIN:
                    event_bits.append('EPOLLIN')
                if event.events & EPOLLOUT == EPOLLOUT:
                    event_bits.append('EPOLLOUT')
                if event.events & EPOLLRDHUP == EPOLLRDHUP:
                    event_bits.append('EPOLLRDHUP')
                if event.events & EPOLLPRI == EPOLLPRI:
                    event_bits.append('EPOLLPRI')
                if event.events & EPOLLERR == EPOLLERR:
                    event_bits.append('EPOLLERR')
                if event.events & EPOLLHUP == EPOLLHUP:
                    event_bits.append('EPOLLHUP')
                if event.data.fd == sfd:
                    fd_name = 'signalfd()'
                elif event.data.fd == stdout_pipe_fd:
                    fd_name = 'stdout pipe2()'
                elif event.data.fd == stderr_pipe_fd:
                    fd_name = 'stderr pipe2()'
                else:
                    fd_name = "???"
                print(" events: {} ({})".format(
                    event.events, ' | '.join(event_bits)))
                print(" fd: {} ({})".format(event.data.fd, fd_name))
                if event.data.fd == sfd:
                    print("signalfd() descriptor ready")
                    if event.events & EPOLLIN:
                        print("Reading data from signalfd()...")
                        # Read the next delivered signal
                        sfd_stream.readinto(fdsi)
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
                                    assert WIFEXITED(waitid_result.si_status)
                                    print("child exited normally")
                                    print("exit code:",
                                          WEXITSTATUS(waitid_result.si_status))
                                    waiting_for.remove('proc')
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
                elif event.data.fd == stdout_pipe_fd:
                    print("pipe() (stdout) descriptor ready")
                    if event.events & EPOLLIN:
                        print("Reading data from stdout...")
                        data = read(stdout_pipe_fd, PIPE_BUF)
                        print("Read {} bytes from stdout".format(len(data)))
                        print(data)
                    if event.events & EPOLLHUP:
                        print("Removing stdout pipe from epoll")
                        epoll_ctl(epollfd, EPOLL_CTL_DEL, stdout_pipe_fd, None)
                        print("Closing stdout pipe")
                        close(stdout_pipe_fd)
                        waiting_for.remove('stdout')
                elif event.data.fd == stderr_pipe_fd:
                    print("pipe() (stderr) descriptor ready")
                    if event.events & EPOLLIN:
                        print("Reading data from stdout...")
                        data = read(stderr_pipe_fd, PIPE_BUF)
                        print("Read {} bytes from stderr".format(len(data)))
                        print(data)
                    if event.events & EPOLLHUP:
                        print("Removing stderr pipe from epoll")
                        epoll_ctl(epollfd, EPOLL_CTL_DEL, stderr_pipe_fd, None)
                        print("Closing stderr pipe")
                        close(stderr_pipe_fd)
                        waiting_for.remove('stderr')
                else:
                    # FIXME: we are still getting weird activation events on fd
                    # 0 (stdin) with events == 0 (nothing). I cannot explain
                    # this yet.
                    print("Unexpected descriptor ready:",
                          event.data.fd)
    assert not waiting_for
    print("Closing epollfd", epollfd)
    close(epollfd)
    print("Unblocking signals")
    sigprocmask(SIG_UNBLOCK, mask, None)
    print("Exiting normally")


if __name__ == '__main__':
    main()
