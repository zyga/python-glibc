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
:mod:`pyglibc._modular` -- modular classes
==========================================

This module contains the :class:`modular_type` class, the
:class:`modular_object` class and the :func:`multiplexed` method decorator.
Together they allow libraries to construct large mix-in master classes that
combine many small classes together.

For example, the :pep:`3156` main loop class contains lots of topic-based
responsibilities.  A concrete implementation might be one, monolithic, class
but doing so would make it harder to read or maintain. Alternatively, the class
that applications use might be composed of a collection of small classes that
implement an encapsulated subset of the functionality.

For example::

    class foo_part(object):

        def do_foo(self):
            pass

    class bar_part(object):

        def do_bar(self):
            pass

    class FooBar(modular_object):
        __modules__ = [foo_part, bar_part]


This works well as long as methods are unique. For better encapsulation at
least ``__init__`` will be implemented in each non-stateless class and calls to
such methods should work correctly. To achieve that, use the ``@multiplexed``
decorator on **all** methods that want to share the same name. This is just a
soft requirement as the call would work in either case, enforcing the presence
of ``@multiplexed`` improves code readability.

For example, let's allow both parts we've defined before to have an
initialization method::

    class foo_part(object):

        @multiplexed
        def __init__(self):
            self.__foo_cnt = 0

        def do_foo(self):
            self.__foo_cnt += 1

    class bar_part(object):

        @multiplexed
        def __init__(self):
            self.__bar_cnt = 0

        def do_foo(self):
            self.__bar_cnt += 1

    class FooBar(modular_object):
        __modules__ = [foo_part, bar_part]

In addition, modules can be composed dynamically using imperative code. For
example, some platform specific modules can be injected into the list of class
modules while keeping the code that does the injection separate from the module
implementation::

    class unix_part(object):

        def handle_stuff(self):
            pass

    class windows_part(object):

        def handle_stuff(self):
            pass

    class Portable(modular_object):
        __modules__ = []
        if sys.platform == 'win32':
            __modules__.append(windows_part)
        else:
            __modules__.append(unix_part)
"""
from __future__ import absolute_import
from __future__ import print_function

import abc
import inspect

__author__ = 'Zygmunt Krynicki <zygmunt.krynicki@canonical.com>'
__all__ = [
    'is_inversed',
    'is_multiplexed',
    'modular_object',
    'modular_type',
    'multiplexed',
]


class bound_multiplexed_method(object):

    __slots__ = ('_instance', '_multiplexed_method')

    def __init__(self, instance, multiplexed_method):
        self._instance = instance
        self._multiplexed_method = multiplexed_method

    @property
    def __name__(self):
        return self._multiplexed_method._name

    def __call__(self, **kwargs):
        """
        Call the multiplexed method

        Calling this method will forward the call, in sequence, to each of the
        multiplexed methods. The return value is always ``None``.
        """
        if self._multiplexed_method._inversed:
            impl_iter = reversed(self._multiplexed_method._impl_list)
        else:
            impl_iter = iter(self._multiplexed_method._impl_list)
        for impl in impl_iter:
            impl(self._instance, **kwargs)


class multiplexed_method(object):
    """
    Multiplexed method dispatcher

    Instances of this class are callable with an object (self) and a list of
    keyword arguments. They will forward the call to all of the implementation
    methods, in sequence. The return value is always None.
    """

    _multiplexed = True  # for is_multiplexed completeness

    def __init__(self, name, impl_list, inversed):
        """
        Initialize a new ``multiplexed_method`` with a method name (for
        debugging) a list of methods to call and a flag that determines the
        call order.
        """
        self._name = name
        self._impl_list = impl_list
        self._inversed = inversed

    @property
    def __name__(self):
        return self._name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return bound_multiplexed_method(instance, self)

    def __repr__(self):
        return "<{} name:{!r} impl_list:{!r} inversed:{!r}>".format(
            self.__class__.__name__, self._name, self._impl_list,
            self._inversed)


def multiplexed(func=None, inversed=False):
    """
    Decorator for multiplexing functions

    Functions decorated with this decorator, when they are a part of a
    :class:`modular_object` subclass, pass down this call to each module
    that implements a method with the same name.

    All implementations need to be annotated with this decorator, or a
    TypeError is raised at class construction time.
    """
    if func is None:
        def decorator(func):
            func._multiplexed = True
            func._inversed = inversed
            return func
        return decorator
    else:
        func._multiplexed = True
        func._inversed = inversed
        return func


def is_multiplexed(func):
    """
    Check if a given function is multiplexed
    """
    return getattr(func, '_multiplexed', False) is True


def is_inversed(func):
    """
    Check if the call order on a given multiplexed function should be reversed
    """
    return is_multiplexed(func) and getattr(func, '_inversed', False) is True


def _err_not_annotated(func):
    raise TypeError("please annotate {!r} with @multiplexed".format(func))


class modular_type(abc.ABCMeta):
    """
    modular type

    Modular type is a subclass of ``type`` that facilitates constructing
    complex classes out of class modules. It handles subclass construction

    .. note::
        modular_type is a subclass of the ``abc.ABCMeta`` type since this is
        what many concrete modular classes will need to check their conformance
        to some ABCMeta-expressed APIs
    """

    def __new__(mcls, name, bases, ns):
        """
        Construct a new modular_type subclass.

        This method will collect all the classes mentioned in __modules__ and
        inject them into the list of base classes.

        In addition, any method that was decorated with @multiplexed, that has
        more than one implementation, is automatically merged and converted
        into a special :class:`multiplexed_method`` descriptor which dispatches
        the call into each implementation.

        All sub-types of this class will gain the '__multiplexedmethods__'
        attribute that contains a frozenset of methods that undergo call
        multiplexing.
        """
        ns_copy = dict(ns)
        modules = ns_copy.get('__modules__', [])
        if modules:
            del ns['__modules__']
        multiplexed_methods = set()  # set of names
        # Inject modules as additional base classes
        bases = tuple(modules + list(bases))
        # Find all previously multiplexed methods in all the base classes
        for base in bases:
            if hasattr(base, '__multiplexedmethods__'):
                multiplexed_methods.update(base.__multiplexedmethods__)
        # Find all methods annotated with @multiplexed in the class name-space
        for meth_name, meth_impl in (
                pair for pair in ns.items() if inspect.isroutine(pair[1])):
            if is_multiplexed(meth_impl):
                multiplexed_methods.add(meth_name)
        # Find all methods annotated with @multiplexed in all the base classes
        for base in bases:
            for meth_name, meth_impl in inspect.getmembers(
                    base, inspect.isroutine):
                if is_multiplexed(meth_impl):
                    multiplexed_methods.add(meth_name)
        # Freeze the set of names of multiplexed methods
        multiplexed_methods = frozenset(multiplexed_methods)
        ns['__multiplexedmethods__'] = multiplexed_methods
        # Inject unfinished multiplexed_method into class name-space
        for meth_name in multiplexed_methods:
            mm = multiplexed_method(meth_name, [], None)
            ns[meth_name] = mm
        # Construct a new class
        cls = super(modular_type, mcls).__new__(mcls, name, bases, ns)
        # Knowing the MRO, determine the order of multiplexing
        for meth_name in multiplexed_methods:
            meth_impl_list = []
            inversed = False
            # Include implementation from the class name-space
            if meth_name in ns_copy:
                meth_impl = ns_copy[meth_name]
                if not is_multiplexed(meth_impl):
                    _err_not_annotated(meth_impl)
                # Keep track of the inversed flag
                inversed |= is_inversed(meth_impl)
                # Keep track of all of the multiplexed methods
                if meth_impl not in meth_impl_list:
                    meth_impl_list.append(meth_impl)
            # Walk the mro to and finish method multiplexing data
            for base in cls.__mro__:
                # Skip classes that don't have this method
                if not hasattr(base, meth_name):
                    continue
                # Skip abstract methods as they probably won't be annotated
                if (hasattr(base, '__abstractmethods__')
                        and meth_name in base.__abstractmethods__):
                    continue
                meth_impl = getattr(base, meth_name)
                # Keep track of the inversed flag
                inversed |= is_inversed(meth_impl)
                # Enforce that all multiplexed methods are decorated, for
                # easier debugging and code inspection.
                if not is_multiplexed(meth_impl):
                    # XXX: How do I inspect for that in a portable way?
                    if repr(meth_impl) != (
                            "<slot wrapper '__init__' of 'object' objects>"):
                        _err_not_annotated(meth_impl)
                # Collect inherited multiplexed_method objects
                if isinstance(meth_impl, multiplexed_method):
                    # Put base multiplexed methods before all the other things
                    # we've collected here.
                    for base_meth_impl in meth_impl._impl_list:
                        if base_meth_impl not in meth_impl_list:
                            meth_impl_list.insert(0, base_meth_impl)
                # Don't collect stuff we have twice, this fixes all of the
                # object.__init__ dupes.
                elif meth_impl not in meth_impl_list:
                    meth_impl_list.append(meth_impl)
            if len(meth_impl_list) == 1:
                # If we have just one method, don't multiplex it
                setattr(cls, meth_name, meth_impl_list[0])
            else:
                # Update multiplexed_method data
                mm = getattr(cls, meth_name)
                assert isinstance(mm, multiplexed_method)
                # Reverse the list, after all, the list contains the most
                # specialized method first and we want to call them from the
                # most basic one first.
                meth_impl_list.reverse()
                mm._impl_list = meth_impl_list
                mm._inversed = inversed
                # Customize the docstring of each multiplexed_method
                mm.__doc__ = """
Multiplexed version of {}()

Calling this method will forward the call to the following methods:
{}
{}
                """.format(
                    meth_name,
                    '\n'.join([' - {}.{}()'.format(
                        getattr(mi, '__module__', 'object'), mi.__name__)
                        for mi in (reversed(meth_impl_list) if inversed else meth_impl_list)]),
                    ("\n.. note:\n\tThis multiplexed method uses reversed call order"
                     if inversed else ""))
        return cls


modular_object = modular_type('modular_object', (object,), {
    '__doc__': """
        modular object

        Modular object is a basic object-like class that is using
        :class:`modular_type` for its meta-class, thus getting new
        capabilities.
    """,
})
