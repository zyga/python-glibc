# Copyright 2014 Canonical Ltd.
# Written by:
#   Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
:mod:`pyglibc._asyncio_abc` -- interfaces for PEP3156 classes
=============================================================

This module contains interfaces for :pep:`3156` compatible event loop
subsystem. They are in early stages of implementation and are entirely
unstable. Having said that, any API mismatches as compared to the upstream
asyncio module will be fixed in favour of the reference implementation.

The only difference that is reserved up front is related to features that might
require the ``yield from`` syntax. Such features will not be supported.
"""
from __future__ import absolute_import

import abc
import sys

if sys.version_info[0] == 2:
    from pyglibc._p2k import Interface
else:
    from pyglibc._p3k import Interface


__author__ = 'Zygmunt Krynicki <zygmunt.krynicki@canonical.com>'
__all__ = [
    'AbstractEventLoop',
    'AbstractEventLoopPolicy',
    'AbstractFuture',
    'AbstractHandle',
]


# Event loop policy
# -----------------


class AbstractEventLoopPolicy(Interface):
    """
    An abstract event loop policy class defined by :PEP:`3156`.
    """

    @abc.abstractmethod
    def get_event_loop(self):
        """
        Get the current event loop.

        :returns:
            A `AbstractEventLoop` associated with the current context.  The
            context is defined as whatever defines the boundary of an event
            loop.
        """

    @abc.abstractmethod
    def set_event_loop(self, event_loop):
        pass

    @abc.abstractmethod
    def new_event_loop(self):
        pass


class AbstractEventLoop(Interface):
    """
    An abstract event loop class defined by :PEP:`3156`.
    """

    # Starting and stopping
    # ---------------------

    @abc.abstractmethod
    def run_forever(self):
        """
        Runs the event loop until stop() is called.

        This cannot be called when the event loop is already running.
        (This has a long name in part to avoid confusion with earlier versions
        of this PEP, where run() had different behavior, in part because there
        are already too many APIs that have a method named run(), and in part
        because there shouldn't be many places where this is called anyway.)
        """

    @abc.abstractmethod
    def run_until_complete(self, future):
        """
        Runs the event loop until the Future is done.

        If the Future is done, its result is returned, or its exception is
        raised. This cannot be called when the event loop is already running.
        """

    @abc.abstractmethod
    def stop(self):
        """
        Stops the event loop as soon as it is convenient. It is fine to
        restart the loop with run_forever() or run_until_complete()
        subsequently; no scheduled callbacks will be lost if this is done.

        .. note::
            stop() returns normally and the current callback is allowed to
            continue. How soon after this point the event loop stops is up
            to the implementation, but the intention is to stop short of
            polling for I/O, and not to run any callbacks scheduled in the
            future; the major freedom an implementation has is how much of
            the "ready queue" (callbacks already scheduled with call_soon())
            it processes before stopping.
        """

    @abc.abstractmethod
    def is_running(self):
        """
        Returns True if the event loop is currently running,
        False if it is stopped.
        """

    @abc.abstractmethod
    def is_closed(self):
        """
        Returns True if the event loop is closed.

        A closed loop cannot be used for anything
        """
        return self.__closed

    @abc.abstractmethod
    def close(self):
        """
        Closes the event loop, releasing any resources it may hold,
        such as the file descriptor used by epoll() or kqueue(), and
        the default executor. This should not be called while the event loop
        is running. After it has been called the event loop should not be
        used again. It may be called multiple times;
        subsequent calls are no-ops.
        """

    # Basic callbacks
    # ---------------

    @abc.abstractmethod
    def call_soon(self, callback, *args):
        """
        This schedules a callback to be called as soon as possible.

        Returns a Handle (see below) representing the callback, whose
        cancel() method can be used to cancel the callback.
        It guarantees that callbacks are called in the order in which they
        were scheduled.
        """

    @abc.abstractmethod
    def call_later(self, delay, callback, *args):
        """
        Arrange for ``callback(*args)`` to be called approximately delay
        seconds in the future, once, unless cancelled.

        Returns a Handle representing the callback, whose cancel() method can
        be used to cancel the callback. Callbacks scheduled in the past or at
        exactly the same time will be called in an undefined order.
        """

    @abc.abstractmethod
    def call_at(self, when, callback, *args):
        """
        This is like call_later(), but the time is expressed as an absolute
        time. Returns a similar Handle. There is a simple equivalency:
        ``loop.call_later(delay, callback, *args)`` is the same as
        ``loop.call_at(loop.time() + delay, callback, *args)``.
        """

    @abc.abstractmethod
    def time(self):
        """
        Returns the current time according to the event loop's clock.

        This may be time.time() or time.monotonic() or some other
        system-specific clock, but it must return a float expressing the time
        in units of approximately one second since some epoch.

        No clock is perfect -- see :PEP:`418`.
        """

    # Thread interaction
    # ------------------

    @abc.abstractmethod
    def call_soon_threadsafe(self, callback, *args):
        """
        Like ``call_soon(callback, *args)``, but when called from another
        thread while the event loop is blocked waiting for I/O, unblocks
        the event loop.

        :returns:
            Returns a Handle.

        This is the only method that is safe to call from another thread.
        (To schedule a callback for a later time in a threadsafe manner,
        you can use
        ``loop.call_soon_threadsafe(loop.call_later, when, callback, *args)``.)

        .. note::
            This is not safe to call from a signal handler (since it may use
            locks). In fact, no API is signal-safe; if you want to handle
            signals, use :meth:`add_signal_handler()` described below.
        """

    @abc.abstractmethod
    def run_in_executor(self, executor, callback, *args):
        """
        Arrange to call ``callback(*args)`` in an executor (see PEP 3148).

        Returns an asyncio.Future instance whose result on success is the
        return value of that call. This is equivalent to::

            wrap_future(executor.submit(callback, *args)).

        If executor is None, the default executor set by set_default_executor()
        is used. If no default executor has been set yet, a ThreadPoolExecutor
        with a default number of threads is created and set as the default
        executor.  (The default implementation uses 5 threads in this case.)
        """

    @abc.abstractmethod
    def set_default_executor(self, executor):
        """
        Set the default executor used by run_in_executor().  The argument must
        be a PEP 3148 Executor instance or None, in order to reset the default
        executor.
        """

    # DNS lookups
    # -----------

    @abc.abstractmethod
    def getaddrinfo(self, host, port, family=0, type=0, proto=0, flags=0):
        """
        Similar to the socket.getaddrinfo() function but returns a Future.

        The Future's result on success will be a list of the same format as
        returned by socket.getaddrinfo(), i.e. a list of (address_family,
        socket_type, socket_protocol, canonical_name, address) where address is
        a 2-tuple (ipv4_address, port) for IPv4 addresses and a 4-tuple
        (ipv4_address, port, flow_info, scope_id) for IPv6 addresses.

        If the family argument is zero or unspecified, the list returned may
        contain a mixture of IPv4 and IPv6 addresses; otherwise the addresses
        returned are constrained by the family value (similar for proto and
        flags).

        The default implementation calls socket.getaddrinfo() using
        run_in_executor(), but other implementations may choose to implement
        their own DNS lookup.

        The optional arguments must be specified as keyword arguments.

        Note: implementations are allowed to implement a subset of the full
        socket.getaddrinfo() interface; e.g. they may not support symbolic port
        names, or they may ignore or incompletely implement the type, proto and
        flags arguments. However, if type and proto are ignored, the argument
        values passed in should be copied unchanged into the return tuples'
        socket_type and socket_protocol elements. (You can't ignore family,
        since IPv4 and IPv6 addresses must be looked up differently.

        The only permissible values for family are socket.AF_UNSPEC (0),
        socket.AF_INET and socket.AF_INET6, and the latter only if it is
        defined by the platform.)
        """

    @abc.abstractmethod
    def getnameinfo(self, sockaddr, flags=0):
        """
        Similar to socket.getnameinfo() but returns a Future.

        The Future's result on success will be a tuple (host, port).  Same
        implementation remarks as for getaddrinfo().
        """

    # Internet connections
    # --------------------

    @abc.abstractmethod
    def create_connection(self, protocol_factory, host, port, **options):
        """
        Creates a stream connection to a given internet host and port.

        This is a task that is typically called from the client side of the
        connection.  It creates an implementation-dependent bidirectional
        stream Transport to represent the connection, then calls
        protocol_factory() to instantiate (or retrieve) the user's Protocol
        implementation, and finally ties the two together. (See below for the
        definitions of Transport and Protocol.)

        The user's Protocol implementation is created or retrieved by calling
        protocol_factory() without arguments(*). The coroutine's result on
        success is the (transport, protocol) pair; if a failure prevents the
        creation of a successful connection, an appropriate exception will be
        raised. Note that when the coroutine completes, the protocol's
        connection_made() method has not yet been called; that will happen when
        the connection handshake is complete.

        (*) There is no requirement that protocol_factory is a class. If your
        protocol class needs to have specific arguments passed to its
        constructor, you can use lambda. You can also pass a trivial lambda
        that returns a previously constructed Protocol instance.

        The <options> are all specified using optional keyword arguments:

        ssl:
            Pass True to create an SSL/TLS transport (by default a plain TCP
            transport is created). Or pass an ssl.SSLContext object to override
            the default SSL context object to be used. If a default context is
            created it is up to the implementation to configure reasonable
            defaults. The reference implementation currently uses
            PROTOCOL_SSLv23 and sets the OP_NO_SSLv2 option, calls
            set_default_verify_paths() and sets verify_mode to CERT_REQUIRED.
            In addition, whenever the context (default or otherwise) specifies
            a verify_mode of CERT_REQUIRED or CERT_OPTIONAL, if a hostname is
            given, immediately after a successful handshake
            ssl.match_hostname(peercert, hostname) is called, and if this
            raises an exception the conection is closed. (To avoid this
            behavior, pass in an SSL context that ha verify_mode set to
            CERT_NONE. But this means you are not secure, and vulnerable to for
            example man-in-the-middle attacks.)

        family, proto, flags:
            Address family, protocol and flags to be passed through to
            getaddrinfo(). These all default to 0, which means "not specified".
            (The socket type is always SOCK_STREAM.) If any of these values are
            not specified, the getaddrinfo() method will choose appropriate
            values. Note: proto has nothing to do with the high-level Protocol
            concept or the protocol_factory argument.

        sock:
            An optional socket to be used instead of using the host, port,
            family, proto and flags arguments. If this is given, host and port
            must be explicitly set to None.

        local_addr:
            If given, a (host, port) tuple used to bind the socket to locally.
            This is rarely needed but on multi-homed servers you occasionally
            need to force a connection to come from a specific address. This is
            how you would do that. The host and port are looked up using
            getaddrinfo().

        server_hostname:
            This is only relevant when using SSL/TLS; it should not be used
            when ssl is not set. When ssl is set, this sets or overrides the
            hostname that will be verified. By default the value of the host
            argument is used. If host is empty, there is no default and you
            must pass a value for server_hostname. To disable hostname
            verification (which is a serious security risk) you must pass an
            empty string here and pass an ssl.SSLContext object whose
            verify_mode is set to ssl.CERT_NONE as the ssl argument.
        """

    @abc.abstractmethod
    def create_server(self, protocol_factory, host, port, **options):
        """
        Enters a serving loop that accepts connections.

        This is a coroutine that completes once the serving loop is set up to
        serve. The return value is a Server object which can be used to stop
        the serving loop in a controlled fashion (see below). Multiple sockets
        may be bound if the specified address allows both IPv4 and IPv6
        connections.

        Each time a connection is accepted, protocol_factory is called without
        arguments(**) to create a Protocol, a bidirectional stream Transport is
        created to represent the network side of the connection, and the two
        are tied together by calling protocol.connection_made(transport).

        (**) See previous footnote for create_connection(). However, since
        protocol_factory() is called once for each new incoming connection, it
        should return a new Protocol object each time it is called.

        The <options> are all specified using optional keyword arguments:

        ssl:
            Pass an ssl.SSLContext object (or an object with the same
            interface) to override the default SSL context object to be used.
            (Unlike for create_connection(), passing True does not make sense
            here -- the SSLContext object is needed to specify the certificate
            and key.)

        backlog:
            Backlog value to be passed to the listen() call. The default is
            implementation-dependent; in the default implementation the default
            value is 100.

        reuse_address:
            Whether to set the SO_REUSEADDR option on the socket. The default
            is True on UNIX, False on Windows.

        family, flags:
            Address family and flags to be passed through to getaddrinfo().
            The family defaults to AF_UNSPEC; the flags default to AI_PASSIVE.
            (The socket type is always SOCK_STREAM; the socket protocol always
            set to 0, to let getaddrinfo() choose.)

        sock:
            An optional socket to be used instead of using the host, port,
            family and flags arguments. If this is given, host and port must be
            explicitly set to None.
        """

    @abc.abstractmethod
    def create_datagram_endpoint(self, protocol_factory, local_addr=None,
                                 remote_addr=None, **options):
        """
        Creates an endpoint for sending and receiving datagrams (typically UDP
        packets). Because of the nature of datagram traffic, there are no
        separate calls to set up client and server side, since usually a single
        endpoint acts as both client and server. This is a coroutine that
        returns a (transport, protocol) pair on success, or raises an exception
        on failure. If the coroutine returns successfully, the transport will
        call callbacks on the protocol whenever a datagram is received or the
        socket is closed; it is up to the protocol to call methods on the
        protocol to send datagrams. The transport returned is a
        DatagramTransport. The protocol returned is a DatagramProtocol. These
        are described later.

        Mandatory positional argument:

        :param protocol_factory:
            A class or factory function that will be called exactly once,
            without arguments, to construct the protocol object to be returned.
            The interface between datagram transport and protocol is described
            below.

        Optional arguments that may be specified positionally or as keyword
        arguments:

        :param local_addr:
            An optional tuple indicating the address to which the socket will
            be bound. If given this must be a (host, port) pair. It will be
            passed to getaddrinfo() to be resolved and the result will be
            passed to the bind() method of the socket created. If getaddrinfo()
            returns more than one address, they will be tried in turn. If
            omitted, no bind() call will be made.

        :param remote_addr:
            An optional tuple indicating the address to which the socket will
            be "connected". (Since there is no such thing as a datagram
            connection, this just specifies a default value for the destination
            address of outgoing datagrams.) If given this must be a (host,
            port) pair. It will be passed to getaddrinfo() to be resolved and
            the result will be passed to sock_connect() together with the
            socket created. If getaddrinfo() returns more than one address,
            they will be tried in turn. If omitted, no sock_connect() call will
            be made.

        The <options> are all specified using optional keyword arguments:

        family, proto, flags:
            Address family, protocol and flags to be passed through to
            getaddrinfo(). These all default to 0, which means "not specified".
            (The socket type is always SOCK_DGRAM.) If any of these values are
            not specified, the getaddrinfo() method will choose appropriate
            values.

        Note that if both local_addr and remote_addr are present, all
        combinations of local and remote addresses with matching address family
        will be tried.
        """

    # Wrapped socket methods
    # ----------------------

    @abc.abstractmethod
    def sock_recv(self, sock, n):
        """
        Receive up to n bytes from socket sock.

        Returns a Future whose result on success will be a bytes object.
        """

    @abc.abstractmethod
    def sock_sendall(self, sock, data):
        """
        Send bytes data to socket sock.

        Returns a Future whose result on success will be None.
        Note: the name uses sendall instead of send, to reflect
        that the semantics and signature of this method echo those
        of the standard library socket method sendall() rather than send().
        """

    @abc.abstractmethod
    def sock_connect(self, sock, address):
        """
        Connect to the given address.

        Returns a Future whose result on success will be None.
        """

    @abc.abstractmethod
    def sock_accept(self, sock):
        """
        Accept a connection from a socket.

        The socket must be in listening mode and bound to an address.
        Returns a Future whose result on success will be a tuple
        (conn, peer) where conn is a connected non-blocking socket
        and peer is the peer address.
        """

    # I/O callbacks
    # -------------

    @abc.abstractmethod
    def add_reader(self, fd, callback, *args):
        """
        Arrange for ``callback(*args)`` to be called whenever file descriptor
        fd is deemed ready for reading. Calling add_reader() again for
        the same file descriptor implies a call to remove_reader()
        for the same file descriptor.
        """

    @abc.abstractmethod
    def add_writer(self, fd, callback, *args):
        """
        Like add_reader(), but registers the callback for writing
        instead of for reading.
        """

    @abc.abstractmethod
    def remove_reader(self, fd):
        """
        Cancels the current read callback for file descriptor fd,
        if one is set.

        If no callback is currently set for the file descriptor, this is
        a no-op and returns False. Otherwise, it removes the callback
        arrangement and returns True.
        """

    @abc.abstractmethod
    def remove_writer(self, fd):
        """
        This is to add_writer() as remove_reader() is to add_reader().
        """

    # Pipes and subprocesses
    # ----------------------
    """
    Fragment of the EventLoop API that deals with pipes and subproceses

    The <options> are all specified using optional keyword arguments:

        stdin:
            Either a file-like object representing the pipe to be
            connected to the subprocess's standard input stream
            using connect_write_pipe(), or the constant subprocess.PIPE
            (the default).

            By default a new pipe will be created and connected.

        stdout:
            Either a file-like object representing the pipe to be
            connected to the subprocess's standard output stream
            using connect_read_pipe(), or the constant subprocess.PIPE
            (the default).

            By default a new pipe will be created and connected.

        stderr:
            Either a file-like object representing the pipe to
            be connected to the subprocess's standard error stream
            using connect_read_pipe(), or one of the constants
            subprocess.PIPE (the default) or subprocess.STDOUT.

            By default a new pipe will be created and connected.
            When subprocess.STDOUT is specified, the subprocess's
            standard error stream will be connected to the same pipe
            as the stdandard output stream.

        bufsize:
            The buffer size to be used when creating a pipe; this
            is passed to subprocess.Popen(). In the default implementation
            this defaults to zero, and on Windows it must be zero;
            these defaults deviate from subprocess.Popen().

        executable, preexec_fn, close_fds, cwd, env, startupinfo,
        creationflags, restore_signals, start_new_session, pass_fds:
            These optional arguments are passed to subprocess.Popen()
            without interpretation.
    """

    @abc.abstractmethod
    def connect_read_pipe(self, protocol_factory, pipe):
        """
        Create a unidrectional stream connection from a file-like
        object wrapping the read end of a UNIX pipe, which must be
        in non-blocking mode. The transport returned is a ReadTransport.
        """

    @abc.abstractmethod
    def connect_write_pipe(self, protocol_factory, pipe):
        """
        Create a unidrectional stream connection from a file-like
        object wrapping the write end of a UNIX pipe, which must be
        in non-blocking mode. The transport returned is a WriteTransport;
        it does not have any read-related methods.
        The protocol returned is a BaseProtocol.
        """

    @abc.abstractmethod
    def subprocess_shell(self, protocol_factory, cmd, **options):
        """
        Create a subprocess from cmd, which is a string using the
        platform's "shell" syntax. This is similar to the standard
        library subprocess.Popen() class called with shell=True.
        The remaining arguments and return value are described below.
        """

    @abc.abstractmethod
    def subprocess_exec(self, protocol_factory, *args, **options):
        """
        Create a subprocess from one or more string arguments, where
        the first string specifies the program to execute, and the
        remaining strings specify the program's arguments. (Thus,
        together the string arguments form the sys.argv value of
        the program, assuming it is a Python script.) This is
        similar to the standard library subprocess.Popen()
        class called with shell=False and the list of strings
        passed as the first argument; however, where Popen()
        takes a single argument which is list of strings,
        subprocess_exec() takes multiple string arguments.
        The remaining arguments and return value are described below.
        """

    # Signal callbacks
    # ----------------

    @abc.abstractmethod
    def add_signal_handler(self, sig, callback, *args):
        """
        Whenever signal sig is received, arrange for ``callback(*args)`` to be
        called. Specifying another callback for the same signal replaces the
        previous handler (only one handler can be active per signal).

        The sig must be a valid sigal number defined in the signal module.  If
        the signal cannot be handled this raises an exception: ValueError if it
        is not a valid signal or if it is an uncatchable signal (e.g. SIGKILL),
        RuntimeError if this particular event loop instance cannot handle
        signals (since signals are global per process, only an event loop
        associated with the main thread can handle signals).
        """

    @abc.abstractmethod
    def remove_signal_handler(self, sig):
        """
        Removes the handler for signal sig, if one is set.

        Raises the same exceptions as add_signal_handler() (except that it may
        return False instead raising RuntimeError for uncatchable signals).

        :returns:
            True if a handler was removed successfully, False if no handler was
            set.
        """


class AbstractHandle(Interface):
    """
    An abstract handle class defined by :PEP:`3156`.

    The various methods for registering one-off callbacks (call_soon(),
    call_later(), call_at() and call_soon_threadsafe()) all return an object
    representing the registration that can be used to cancel the callback.

    This object is called a Handle. Handles are opaque and have only one public
    method:

    Note that add_reader(), add_writer() and add_signal_handler() do not return
    Handles.
    """

    @abc.abstractmethod
    def cancel(self):
        """
        Cancel the callback
        """


class AbstractFuture(Interface):
    """
    An abstract future class defined by :PEP:`3156`.
    """

    @abc.abstractmethod
    def cancel(self):
        """
        If the Future is already done (or cancelled), do nothing and return
        False. Otherwise, this attempts to cancel the Future and returns True.

        If the the cancellation attempt is successful, eventually the Future's
        state will change to cancelled (so that cancelled() will return True)
        and the callbacks will be scheduled.  For regular Futures, cancellation
        will always succeed immediately; but for Tasks (see below) the task may
        ignore or delay the cancellation attempt.
        """

    @abc.abstractmethod
    def cancelled(self):
        """"
        Returns True if the Future was successfully cancelled.
        """

    @abc.abstractmethod
    def done(self):
        """
        Returns True if the Future is done.

        Note that a cancelled Future is considered done too (here and
        everywhere).
        """

    @abc.abstractmethod
    def result(self):
        """
        Returns the result set with set_result(), or raises the exception
        set with set_exception().

        Raises CancelledError if cancelled. Difference with PEP 3148: This has
        no timeout argument and does not wait; if the future is not yet done,
        it raises an exception.
        """

    @abc.abstractmethod
    def exception(self):
        """
        Returns the exception if set with set_exception(), or None if a result
        was set with set_result().

        Raises CancelledError if cancelled. Difference with PEP 3148: This has
        no timeout argument and does not wait; if the future is not yet done,
        it raises an exception.
        """

    @abc.abstractmethod
    def add_done_callback(self, fn):
        """
        Add a callback to be run when the Future becomes done (or is
        cancelled).

        If the Future is already done (or cancelled), schedules the callback to
        using call_soon().

        Difference with :PEP:`3148`: The callback is never called immediately,
        and always in the context of the caller -- typically this is a thread.

        You can think of this as calling the callback through call_soon().

        Note that in order to match PEP:`3148`, the callback (unlike all other
        callbacks defined in :PEP:`3156`, and ignoring the convention from the
        section "Callback Style" below) is always called with a single
        argument, the Future object. (The motivation for strictly serializing
        callbacks scheduled with call_soon() applies here too.)
        """

    @abc.abstractmethod
    def remove_done_callback(self, fn):
        """
        Remove the argument from the list of callbacks.

        This method is not defined by :PEP:`3148`.  The argument must be equal
        (using ==) to the argument passed to add_done_callback().

        Returns the number of times the callback was removed.
        """

    @abc.abstractmethod
    def set_result(self, result):
        """
        The Future must not be done (nor cancelled) already.

        This makes the Future done and schedules the callbacks.
        Difference with :PEP:`3148`: This is a public API.
        """

    @abc.abstractmethod
    def set_exception(self, exception):
        """
        The Future must not be done (nor cancelled) already.

        This makes the Future done and schedules the callbacks.
        Difference with PEP 3148: This is a public API.
        """
