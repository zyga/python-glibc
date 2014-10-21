#define _GNU_SOURCE

#include <stdlib.h>
#include <stdio.h>

#include <sys/epoll.h>
#include <sys/timerfd.h>
#include <sys/signalfd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <signal.h>
#include <unistd.h>
#include <limits.h>
#include <string.h>


int main(int argc, char *argv[]) {
    sigset_t mask;
    if (sigemptyset(&mask) == -1) {
        perror("sigemptyset");
        return EXIT_FAILURE;
    }
    if (sigaddset(&mask, SIGINT) == -1) {
        perror("sigaddset SIGINT");
        return EXIT_FAILURE;
    }
    if (sigaddset(&mask, SIGQUIT) == -1) {
        perror("sigaddset SIGQUIT");
        return EXIT_FAILURE;
    }
    if (sigaddset(&mask, SIGCHLD) == -1) {
        perror("sigaddset SIGCHLD");
        return EXIT_FAILURE;
    }
    if (sigaddset(&mask, SIGPIPE) == -1) {
        perror("sigaddset SIGPIPE");
        return EXIT_FAILURE;
    }
    printf("Blocking signals\n");
    if (sigprocmask(SIG_BLOCK, &mask, NULL) == 1) {
        perror("sigprocmask");
        return EXIT_FAILURE;
    }
    int sfd = signalfd(-1, &mask, SFD_CLOEXEC);
    if (sfd == -1) {
        perror("signalfd");
        return EXIT_FAILURE;
    }
    printf("Got signalfd %d\n", sfd);
    int epollfd = epoll_create1(EPOLL_CLOEXEC);
    if (epollfd == -1) {
        perror("epoll_create1");
        return EXIT_FAILURE;
    }
    printf("Got epollfd %d\n", epollfd);
    struct epoll_event ev;
    ev.events = EPOLLIN;
    ev.data.fd = sfd;
    printf("Adding signalfd fd %d to epoll\n", sfd);
    if (epoll_ctl(epollfd, EPOLL_CTL_ADD, sfd, &ev) == -1) {
        perror("epoll_ctl EPOLL_CTL_ADD sfd");
        return EXIT_FAILURE;
    }
    int stdout_pair[2];
    pipe2(stdout_pair, O_CLOEXEC);
    printf("Got stdout pipe pair %d %d\n", stdout_pair[0], stdout_pair[1]);
    ev.events = EPOLLIN | EPOLLHUP | EPOLLERR | EPOLLRDHUP | EPOLLOUT | EPOLLPRI;
    ev.data.fd = stdout_pair[0];
    printf("Adding pipe fd %d to epoll\n", stdout_pair[0]);
    if (epoll_ctl(epollfd, EPOLL_CTL_ADD, stdout_pair[0], &ev) == -1) {
        perror("epoll_ctl EPOLL_CTL_ADD stdout_pair[0]");
        return EXIT_FAILURE;
    }
    int stderr_pair[2];
    pipe2(stderr_pair, O_CLOEXEC);
    printf("Got stderr pipe pair %d %d\n", stderr_pair[0], stderr_pair[1]);
    ev.events = EPOLLIN | EPOLLHUP | EPOLLERR | EPOLLRDHUP | EPOLLERR | EPOLLPRI;
    ev.data.fd = stderr_pair[0];
    printf("Adding pipe fd %d to epoll\n", stderr_pair[0]);
    if (epoll_ctl(epollfd, EPOLL_CTL_ADD, stderr_pair[0], &ev) == -1) {
        perror("epoll_ctl EPOLL_CTL_ADD stderr_pair[0]");
        return EXIT_FAILURE;
    }
    pid_t pid = fork();
    switch (pid) {
        case -1:
            perror("fork");
            return EXIT_FAILURE;
        case 0:
            /* child */
            if (dup3(stdout_pair[1], 1, 0) == -1) {
                perror("dup3 stdout_pair");
                return EXIT_FAILURE;
            }
            if (dup3(stderr_pair[1], 2, 0) == -1) {
                perror("dup3 stderr_pair");
                return EXIT_FAILURE;
            }
            if (argc >= 2)
                execvp(argv[1], argv+1);
            else {
                char * const usage[] = {"echo", "usage: demo3 PROG [ARGS]", ""};
                execvp(usage[0], usage);
            }
            return EXIT_FAILURE;
        default:
            if (close(stdout_pair[1]) == -1) {
                perror("close stdout_pair[1]");
                return EXIT_FAILURE;
            }
            if (close(stderr_pair[1]) == -1) {
                perror("close stderr_pair[1]");
                return EXIT_FAILURE;
            }
            break;
    }
    struct {
        unsigned stdout:1;
        unsigned stderr:1;
        unsigned proc:1;
    } waiting_for = {
        .stdout = 1,
        .stderr = 1,
        .proc = 1
    };
    while (waiting_for.stdout || waiting_for.stderr || waiting_for.proc) {
        int MAX_EVENTS = 10;
        struct epoll_event event_array[MAX_EVENTS];
        printf("Waiting for events...");
        if (waiting_for.stdout)
            printf(" stdout");
        if (waiting_for.stderr)
            printf(" stderr");
        if (waiting_for.proc)
            printf(" proc");
        printf("\n");
        int nfds = epoll_wait(epollfd, event_array, MAX_EVENTS, -1);
        if (nfds == -1) {
            perror("epoll_wait");
            return EXIT_FAILURE;
        }
        for (int event_id=0; event_id < nfds; ++event_id) {
            const struct epoll_event *event = &event_array[event_id];
            printf("[event %d]\n", event_id);
            printf(" events: %d (", event->events);
            if (event->events & EPOLLIN) printf(" EPOLLIN");
            if (event->events & EPOLLOUT) printf(" EPOLLOUT");
            if (event->events & EPOLLHUP) printf(" EPOLLHUP");
            if (event->events & EPOLLERR) printf(" EPOLLERR");
            if (event->events & EPOLLRDHUP) printf(" EPOLRDHUP");
            if (event->events & EPOLLPRI) printf(" EPOLLPRI");
            printf(")\n");
            printf(" fd: %d (", event->data.fd);
            if (event->data.fd == sfd)
                printf("signalfd()");
            else if (event->data.fd == stdout_pair[0])
                printf("stdout pipe2()");
            else if (event->data.fd == stderr_pair[0])
                printf("stderr pipe2()");
            else
                printf("???");
            printf(")\n");
            if (event->data.fd == sfd) {
                printf("signalfd() descriptor ready\n");
                if (event->events & EPOLLIN) {
                    printf("Reading data from signalfd()...\n");
                    struct signalfd_siginfo fdsi;
                    if (read(sfd, &fdsi, sizeof(fdsi)) != sizeof(fdsi)) {
                        perror("read sfd");
                        return EXIT_FAILURE;
                    }
                    switch (fdsi.ssi_signo) {
                        case SIGINT:
                            printf("Got SIGINT\n");
                            break;
                        case SIGQUIT:
                            printf("Got SIGQUIT\n");
                            return EXIT_SUCCESS;
                        case SIGCHLD:
                            printf("Got SIGCHLD\n");
                            siginfo_t waitid_result;
                            memset(&waitid_result, 0, sizeof waitid_result);
                            if (waitid(P_PID, pid, &waitid_result, WNOHANG |
                                       WEXITED | WSTOPPED| WCONTINUED |
                                       WUNTRACED) == -1) {
                                perror("waitid");
                                return EXIT_FAILURE;
                            }
                            /* FIXME: how does waitid say that child isn't
                             * ready when WNOHANG is used (as we do). The man
                             * page claims it returns 0 in such a case. */
                            printf("child event\n");
                            printf("si_pid: %d\n", waitid_result.si_pid);
                            printf("si_uid: %d\n", waitid_result.si_uid);
                            printf("si_signo: %d\n", waitid_result.si_signo);
                            printf("si_status: %d\n", waitid_result.si_status);
                            printf("si_code: %d\n", waitid_result.si_code);
                            switch (waitid_result.si_code) {
                                case CLD_EXITED:
                                    printf("child exited normally\n");
                                    printf("exit code: %d\n",
                                           WEXITSTATUS(waitid_result.si_status));
                                    waiting_for.proc = 0;
                                    /* NOTE: I think this is essentially flawed.
                                     *
                                     * The pipes we give out can live on as we
                                     * hand them down and the child process can fork
                                     * and also hand them down. We cannot be sure
                                     * that we have "all" of the output and that "enough"
                                     * time has passed. I think that we should simply
                                     * close those pipes as soon as this happens.
                                     *
                                     * Perhaps we should also read all the
                                     * remaining bytes (though if the runaway
                                     * processes are faster than us that will
                                     * also never finish in a pessimistic case)
                                     * but this would need non-blocking support
                                     * first. */
                                    if (waiting_for.stdout) {
                                        epoll_ctl(epollfd, EPOLL_CTL_DEL,
                                                  stdout_pair[0], NULL);
                                        close(stdout_pair[0]);
                                        waiting_for.stdout = 0;
                                    }
                                    if (waiting_for.stderr) {
                                        epoll_ctl(epollfd, EPOLL_CTL_DEL,
                                                  stderr_pair[0], NULL);
                                        close(stderr_pair[0]);
                                        waiting_for.stderr = 0;
                                    }
                                    break;
                                case CLD_KILLED:
                                    printf("child was killed by signal\n");
                                    printf("death signal: %d\n", waitid_result.si_status);
                                    waiting_for.proc = 0;
                                    break;
                                case CLD_DUMPED:
                                    printf("core: %d\n",
                                          WCOREDUMP(waitid_result.si_status));
                                    break;
                                case CLD_STOPPED:
                                    printf("child was stopped\n");
                                    printf("stop signal: %d\n",
                                               waitid_result.si_status);
                                    break;
                                case CLD_TRAPPED:
                                    printf("child was trapped\n");
                                    /* TODO: we could explore trap stuff here */
                                case CLD_CONTINUED:
                                    printf("child was continued\n");
                                    break;
                                default:
                                    printf("Unknown CLD_ code: %d\n",
                                           waitid_result.si_code);
                                    return EXIT_FAILURE;
                            }
                            break;
                        case SIGPIPE:
                            printf("Got SIGPIPE\n");
                            break;
                        default:
                            printf("Got signal %d\n", fdsi.ssi_signo);
                            break;
                    }
                }
            } else if (event->data.fd == stdout_pair[0]) {
                printf("pipe() (stdout) descriptor ready\n");
                if (event->events & EPOLLIN) {
                    printf("Reading data from stdout...\n");
                    char buf[PIPE_BUF];
                    ssize_t num_read = read(stdout_pair[0], buf, sizeof buf);
                    if (num_read == -1) {
                        perror("read stdout");
                        return EXIT_FAILURE;
                    }
                    printf("Read %zd bytes from stdout\n", num_read);
                    fwrite(buf, 1, num_read, stdout);
                }
                if (event->events & EPOLLHUP) {
                    printf("Removing stdout pipe from epoll\n");
                    epoll_ctl(epollfd, EPOLL_CTL_DEL, stdout_pair[0], NULL);
                    printf("Closing stdout pipe\n");
                    close(stdout_pair[0]);
                    waiting_for.stdout = 0;
                }
            } else if (event->data.fd == stderr_pair[0]) {
                printf("pipe() (stderr) descriptor ready\n");
                if (event->events & EPOLLIN) {
                    printf("Reading data from stderr...\n");
                    char buf[PIPE_BUF];
                    ssize_t num_read = read(stderr_pair[0], buf, sizeof buf);
                    if (num_read == -1) {
                        perror("read stderr");
                        return EXIT_FAILURE;
                    }
                    printf("Read %zd bytes from stderr\n", num_read);
                    fwrite(buf, 1, num_read, stderr);
                }
                if (event->events & EPOLLHUP) {
                    printf("Removing stderr pipe from epoll\n");
                    epoll_ctl(epollfd, EPOLL_CTL_DEL, stderr_pair[0], NULL);
                    printf("Closing stderr pipe\n");
                    close(stderr_pair[0]);
                    waiting_for.stderr = 0;
                }
            } else {
                printf("Unexpected descriptor ready: %d\n", event->data.fd);
            }
        }
    }
    goto cleanup;
cleanup:
    if (close(sfd) == -1) {
        perror("close(sfd)");
        return EXIT_FAILURE;
    }
    if (close(epollfd) == -1) {
        perror("close(epollfd)");
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
