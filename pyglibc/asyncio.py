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
:mod:`pyglibc.asyncio` -- reimplementation of PEP3156 asyncio
=============================================================

This module is considered stable public API. It will maintain backwards
compatibility for the foreseeable future. Any changes will be made to conform
more strictly with the original specification and the reference implementation
present in the python standard library.

Specification
-------------

Specification of a PEP-compliant (or partially compliant as not all fragments
are implemented at this time) event loop mechanism. This includes the EventLoop
class, supporting Handle and Future classes as well as a group of exceptions.

This specification is designed to ease verification of the implementation built
into plainbox, for the purpose of being portable to python3.2 (unlike the
reference, provisional implementation which requires python3.3) and well
understood by plainbox maintainers (unlike the myriad of existing mainloop
systems developed inside other projects).

Eventually, we might drop this whole package, and require python3.4, or perhaps
some future python version that promises API stability for the asyncio module.

The specification is structured as a group of classes inheriting from
:class:`IEventLoopFragment`. A conforming implementation will inherit from the
specific fragments (ideally from all the non-optional) fragments, and provide
concrete implementation of each method.

Event Loop Management
---------------------

Event loop management is controlled by an event loop policy, which is a global
(per-process) object. There is a default policy, and an API to change the
policy. A policy defines the notion of context; a policy manages a separate
event loop per context. The default policy's notion of context is defined as
the current thread.

Certain platforms or programming frameworks may change the default policy to
something more suitable to the expectations of the users of that platform or
framework. Such platforms or frameworks must document their policy and at what
point during their initialization sequence the policy is set, in order to avoid
undefined behavior when multiple active frameworks want to override the default
policy. (See also "Embedded Event Loops" below.)

To get the event loop for current context, use get_event_loop(). This returns
an event loop object implementing the interface specified below, or raises an
exception in case no event loop has been set for the current context and the
current policy does not specify to create one. It should never return None.

To set the event loop for the current context, use set_event_loop(event_loop),
where event_loop is an event loop object, i.e. an instance of
AbstractEventLoop, or None. It is okay to set the current event loop to None,
in which case subsequent calls to get_event_loop() will raise an exception.
This is useful for testing code that should not depend on the existence of a
default event loop.

It is expected that get_event_loop() returns a different event loop object
depending on the context (in fact, this is the definition of context). It may
create a new event loop object if none is set and creation is allowed by the
policy. The default policy will create a new event loop only in the main thread
(as defined by threading.py, which uses a special subclass for the main
thread), and only if get_event_loop() is called before set_event_loop() is ever
called. (To reset this state, reset the policy.) In other threads an event loop
must be explicitly set. Other policies may behave differently. Event loop by
the default policy creation is lazy; i.e. the first call to get_event_loop()
creates an event loop instance if necessary and specified by the current
policy.

For the benefit of unit tests and other special cases there's a third policy
function: new_event_loop(), which creates and returns a new event loop object
according to the policy's default rules. To make this the current event loop,
you must call set_event_loop() with it.

To change the event loop policy, call set_event_loop_policy(policy), where
policy is an event loop policy object or None. If not None, the policy object
must be an instance of AbstractEventLoopPolicy that defines methods
get_event_loop(), set_event_loop(loop) and new_event_loop(), all behaving like
the functions described above.

Passing a policy value of None restores the default event loop policy
(overriding the alternate default set by the platform or framework). The
default event loop policy is an instance of the class DefaultEventLoopPolicy.
The current event loop policy object can be retrieved by calling
get_event_loop_policy().
"""
from __future__ import absolute_import

from pyglibc._asyncio_policy import DefaultEventLoopPolicy
from pyglibc._asyncio_policy import get_event_loop
from pyglibc._asyncio_policy import get_event_loop_policy
from pyglibc._asyncio_policy import new_event_loop
from pyglibc._asyncio_policy import set_event_loop
from pyglibc._asyncio_policy import set_event_loop_policy

__author__ = 'Zygmunt Krynicki <zygmunt.krynicki@canonical.com>'
__all__ = [
    'DefaultEventLoopPolicy',
    'get_event_loop',
    'get_event_loop_policy',
    'new_event_loop',
    'set_event_loop',
    'set_event_loop_policy',
]
