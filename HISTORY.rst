0.6 (2014-11-09)
================

* Functions from the pthread library are now supported
* Added functions: ``read(2)``, ``pause(2)``, ``eventfd(2)``,
  ``eventfd_read(2)``, ``eventfd_write(2)``, ``clock_getres(2)``,
  ``clock_gettime(2)`` and ``clock_settime(2)``.
* Added constants: ``NSIG``, ``EFD_CLOEXEC``, ``EFD_NONBLOCK``,
  ``EFD_SEMAPHORE``, ``CLOCK_REALTIME``, ``CLOCK_MONOTONIC``,
  ``CLOCK_PROCESS_CPUTIME_ID``, ``CLOCK_THREAD_CPUTIME_ID``,
  ``CLOCK_MONOTONIC_RAW``, ``CLOCK_REALTIME_COARSE``,
  ``CLOCK_MONOTONIC_COARSE``, ``CLOCK_BOOTTIME``, ``CLOCK_REALTIME_ALARM``,
  ``CLOCK_BOOTTIME_ALARM``,
* Added new module :mod:`pyglibc.select` that contains a Python 2.7+ version of the
  select.py from Python 3.4. This module contains a pure-python version of the
  ``epoll`` class. It may be used in place of the module from the standard
  library if additional features are desired in a cross-python-version portable
  manner.
* Added new module :mod:`pyglibc.selectors` that contains a Python 2.7+ version
  of the selectors.py from Python 3.4. As with pyglibc.select, it can be used
  in place of the original.
* Added new module :mod:`pyglibc._signalfd` that exposes ``signalfd(2)`` in a
  much more pythonic way. Use signalfd as a file, as a context manager, inspect
  it in pdb, all easily without having to browse through manual pages. It is
  exposed as ``pyglibc.signalfd`` for easier importing.
* Added new module :mod:`pyglibc._pthread_sigmask` that exposes
  ``pthread_sigmask(2)`` in a much more pythonic way, making it a perfect
  companion for the ``signalfd()`` class. It is exposed as
  ``pyglibc.pthread_sigmask`` for easier importing.
* Added new module :mod:`pyglibc._pipe` that expoes ``pipe2(2)`` in the same
  way as Python 3.4 does via the ``os.pipe()`` and ``os.pipe2()`` functions.
* Added new module :mod:`pyglibc._subreaper` that adds pythonic API to
  ``prctl(PR_{GET,SET}_CHILD_SUBREAPER, ...)``. This module exposes a single
  instance called ``subreaper``.

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
