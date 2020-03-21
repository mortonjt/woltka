#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# Copyright (c) 2020--, Qiyun Zhu.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

"""Generic utility functions that are not specific to certain bioinformatics
operations.
"""


def update_dict(dic, other):
    """Update one dictionary with another while checking conflicting items.

    Parameters
    ----------
    dic : dict
        Dictionary to be updated.
    other : dict
        Dictionary as source of new items.

    Raises
    ------
    AssertionError
        Two dictionaries have conflicting values of the same key.

    Notes
    -----
    If conflict-checking is not necessary, one should use Python's built-in
    method `update`.
    """
    for key, value in other.items():
        try:
            assert dic[key] == value, f'Conflicting values found for "{key}".'
        except KeyError:
            dic[key] = value


def add_dict(dic, other):
    """Combine one dictionary with another, adding values for common keys.

    Parameters
    ----------
    dic : dict
        Dictionary to be updated.
    other : dict
        Dictionary as source of new items.
    """
    for key, value in other.items():
        dic[key] = dic.get(key, 0) + value


def intize(dic, zero=False):
    """Convert a dictionary of numbers to integers.

    Parameters
    ----------
    dic : dict
        Input dictionary.
    zero : bool, optional
        Whether keep zero values.
    """
    todel = []
    for key, value in dic.items():
        intval = round(value)
        if intval or zero:
            dic[key] = intval
        else:
            todel.append(key)
    for key in todel:
        del dic[key]


def delnone(dic):
    """Delete None key if any from a dictionary.

    Parameters
    ----------
    dic : dict
        Input dictionary.
    """
    try:
        del dic[None]
    except KeyError:
        pass


def allkeys(dic):
    """Get all keys in a dict of dict.

    Parameters
    ----------
    dic : dict
        Input dictionary.

    Returns
    -------
    set
        Keys.
    """
    return set().union(*dic.values())


def count_list(lst):
    """Count occurrences of elements of a list and return a dictionary.

    Parameters
    ----------
    lst : list
        Input list.

    Returns
    -------
    dict
        Element-to-count map.
    """
    res = {}
    for x in lst:
        res[x] = res.get(x, 0) + 1
    return res


def last_value(lst):
    """Get last value which is not None from a list.

    Parameters
    ----------
    lst : list
        Input list.

    Returns
    -------
    scalar or None
        Last element which is not None, or None if not found.
    """
    try:
        return next(x for x in reversed(lst) if x is not None)
    except StopIteration:
        pass
