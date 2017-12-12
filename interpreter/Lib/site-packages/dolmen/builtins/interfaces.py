# -*- coding: utf-8 -*-

from zope.interface import Interface, classImplements


class IString(Interface):
    """Marker interface for mutable strings.
    """
classImplements(str, IString)


class IUnicode(Interface):
    """Marker interface for mutable unicode strings.
    """
classImplements(unicode, IUnicode)


class INumeric(Interface):
    """Marker interface for a numeric value.
    """
classImplements(int, INumeric)
classImplements(long, INumeric)
classImplements(float, INumeric)


class IBoolean(Interface):
    """Marker interface for a boolean.
    """
classImplements(bool, IBoolean)


class IIterable(Interface):
    """Base interface for iterable types.
    """

    def __iter__():
        """Return an iterator object.
        """


class IList(IIterable):
    """Marker interface for lists
    """
classImplements(list, IList)


class ITuple(IIterable):
    """Marker interface for immutable lists
    """
classImplements(tuple, ITuple)


class IDict(IIterable):
    """Marker interface for dicts
    """

    def items():
        """Returns an iterable list of couples key - value,
        as a list of tuples.
        """

    def values():
        """Returns an iterable list of the dict values.
        """

    def keys():
        """Returns an iterable list of the dict keys.
        """

    def has_key(key):
        """Returns a boolean, True if the key exists in the dict,
        False otherwise.
        """
classImplements(dict, IDict)


class IFile(Interface):
    """Defines an python file builtin.
    """

    def seek(offset, whence=0):
        """Set the file's current position.
        """

    def read(size):
        """Read at most size bytes from the file.
        """

    def readline(length=None):
        """Read one entire line from the file.
        """

    def readlines(sizehint=0):
        """Read until EOF using readline() and return a list
        containing the lines thus read.
        """

    def write(s):
        """Write a string to the file.
        """

    def writelines(iterable):
        """Write a sequence of strings to the file.
        """

    def tell():
        """Return the file's current position.
        """

    def truncate(size=None):
        """Truncate the file's size.
        """
classImplements(file, IFile)


__all__ = ("IString", "IUnicode", "IBoolean", "INumeric",
           "IIterable", "IList", "ITuple", "IDict", "IFile")
