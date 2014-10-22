0.5 (2014-10-22)
================

* Added tests for structure / union size and offset of each field
* New feature, type aliases for non-compound types like ``time_t``.
* Added functions: ``prctl(2)``, ``timerfd_create(2)``, ``timerfd_settime(2)``,
  ``timerfd_gettime(2)``.
* Added constants: ``PR_SET_PDEATHSIG``, ``PR_GET_PDEATHSIG``,
  ``PR_GET_DUMPABLE``, ``PR_SET_DUMPABLE``, ``PR_GET_UNALIGN``,
  ``PR_SET_UNALIGN``, ``PR_GET_KEEPCAPS``, ``PR_SET_KEEPCAPS``,
  ``PR_GET_FPEMU``, ``PR_SET_FPEMU``, ``PR_GET_FPEXC``, ``PR_SET_FPEXC``,
  ``PR_GET_TIMING``, ``PR_SET_TIMING``, ``PR_SET_NAME``, ``PR_GET_NAME``,
  ``PR_GET_ENDIAN``, ``PR_SET_ENDIAN``, ``PR_GET_SECCOMP``, ``PR_SET_SECCOMP``,
  ``PR_CAPBSET_READ``, ``PR_CAPBSET_DROP``, ``PR_GET_TSC``, ``PR_SET_TSC``,
  ``PR_GET_SECUREBITS``, ``PR_SET_SECUREBITS``, ``PR_SET_TIMERSLACK``,
  ``PR_GET_TIMERSLACK``, ``PR_TASK_PERF_EVENTS_DISABLE``,
  ``PR_TASK_PERF_EVENTS_ENABLE``, ``PR_MCE_KILL``, ``PR_MCE_KILL_GET``,
  ``PR_SET_MM``, ``PR_SET_CHILD_SUBREAPER``, ``PR_GET_CHILD_SUBREAPER``,
  ``PR_SET_NO_NEW_PRIVS``, ``PR_GET_NO_NEW_PRIVS``, ``PR_GET_TID_ADDRESS``,
  ``PR_SET_THP_DISABLE``, ``PR_GET_THP_DISABLE``, ``PR_UNALIGN_NOPRINT``,
  ``PR_UNALIGN_SIGBUS``, ``PR_FPEMU_NOPRINT``, ``PR_FPEMU_SIGFPE``,
  ``PR_FP_EXC_SW_ENABLE``, ``PR_FP_EXC_DIV``, ``PR_FP_EXC_OVF``,
  ``PR_FP_EXC_UND``, ``PR_FP_EXC_RES``, ``PR_FP_EXC_INV``,
  ``PR_FP_EXC_DISABLED``, ``PR_FP_EXC_NONRECOV``, ``PR_FP_EXC_ASYNC``,
  ``PR_FP_EXC_PRECISE``, ``PR_TIMING_STATISTICAL``, ``PR_TIMING_TIMESTAMP``,
  ``PR_ENDIAN_BIG``, ``PR_ENDIAN_LITTLE``, ``PR_ENDIAN_PPC_LITTLE``,
  ``PR_TSC_ENABLE``, ``PR_TSC_SIGSEGV``, ``PR_MCE_KILL_CLEAR``,
  ``PR_MCE_KILL_SET``, ``PR_MCE_KILL_LATE``, ``PR_MCE_KILL_EARLY``,
  ``PR_MCE_KILL_DEFAULT``, ``PR_SET_MM_START_CODE``, ``PR_SET_MM_END_CODE``,
  ``PR_SET_MM_START_DATA``, ``PR_SET_MM_END_DATA``, ``PR_SET_MM_START_STACK``,
  ``PR_SET_MM_START_BRK``, ``PR_SET_MM_BRK``, ``PR_SET_MM_ARG_START``,
  ``PR_SET_MM_ARG_END``, ``PR_SET_MM_ENV_START``, ``PR_SET_MM_ENV_END``,
  ``PR_SET_MM_AUXV``, ``PR_SET_MM_EXE_FILE``, ``PR_SET_PTRACER``,
  ``PR_SET_PTRACER_ANY``, ``TFD_TIMER_ABSTIME``, ``TFD_CLOEXEC``
  and ``TFD_NONBLOCK``,
* Added structures: ``struct itimerspec``, ``struct timespec`` and
  ``struct timeval``.
* Added type alias for ``time_t`` and ``suseconds_t``

0.4 (2014-10-21)
================

* Started tracking changes relevant to other people.
* First release with tests for constants and type sizes.
* Fixed issues with ``struct epoll_event`` (size mismatch).
* Added functions: ``close(2)``.
* Added constants: ``FD_SETSIZE``, ``EPOLLRDNORM``, ``EPOLLRDBAND``,
  ``EPOLLWRNORM``, ``EPOLLWRBAND``, ``EPOLLMSG``.
* Improved bundled demos (not part of release)
