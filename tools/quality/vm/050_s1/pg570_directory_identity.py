"""BUG860/YKT629: borrowed dir FD and pathname must still name one owned directory.

This is an identity check, never a capability/Root grant. Caller separately
requires root uid/gid/0700/noACL. Never follows a swapped symlink.
"""
import os
import stat


def identity(value):
    return (value.st_dev, value.st_ino, value.st_uid, value.st_gid, value.st_mode, value.st_nlink)


def held_directory(fd, path, expected):
    if type(fd) is not int or fd < 0 or type(expected) is not tuple or len(expected) != 6:
        raise ValueError('borrowed directory unavailable')
    if any(type(v) is not int for v in expected) or not stat.S_ISDIR(expected[4]):
        raise ValueError('borrowed directory metadata unavailable')
    actual = os.fstat(fd)
    named = os.stat(path, follow_symlinks=False)
    if not stat.S_ISDIR(actual.st_mode) or identity(actual) != expected or identity(named) != expected:
        raise ValueError('borrowed directory identity changed')


def fully_absent(path):
    return not os.path.lexists(path)
