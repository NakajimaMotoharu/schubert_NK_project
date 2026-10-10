"""SSC262 fixed ordinary current exchange primitive; caller owns admission proof."""
import os
import stat
import ctypes
from pg1088_cold_exchange_io import _native,linked_attributes


def exchange(directory,stage,call=_native):
    if type(directory)is not int or directory<0 or type(stage)is not str or stage!='pg1305-current.part'or not callable(call):
        raise ValueError('fixed ordinary exchange arguments required')
    if not stat.S_ISDIR(os.fstat(directory).st_mode):raise ValueError('held directory required')
    result,error=call(directory,stage)
    if result!=0:raise OSError(error,'ordinary exchange failed; no state inference or retry')


def _native_move(directory,private_directory):
    libc=ctypes.CDLL(None,use_errno=True);rename=libc.renameat2
    rename.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint]
    rename.restype=ctypes.c_int;ctypes.set_errno(0)
    value=rename(directory,b'pg1305-current.part',private_directory,b'current-link.private',1)
    return value,ctypes.get_errno()


def move_old_link(directory,private_directory,held,call=_native_move):
    """Only caller's linked old inode moves; exchange is never repeated here."""
    if any(type(fd)is not int or fd<0 for fd in [directory,private_directory,held])or not callable(call):
        raise ValueError('held current/private descriptors required')
    if any(not stat.S_ISDIR(os.fstat(fd).st_mode)for fd in [directory,private_directory]):
        raise ValueError('held current/private directories required')
    first=linked_attributes(directory,'pg1305-current.part',held)
    if first['target']!='/opt/schubert-nk/releases/0.1.0-PG1068':raise ValueError('old fixed source link required')
    # Destination must be absent, not a replacement or a symlink-followed path.
    try:os.stat('current-link.private',dir_fd=private_directory,follow_symlinks=False)
    except FileNotFoundError:pass
    else:raise FileExistsError('old link preservation destination exists')
    if os.fstat(directory).st_dev!=os.fstat(private_directory).st_dev:
        raise ValueError('same filesystem preservation required')
    value,error=call(directory,private_directory)
    if value!=0:raise OSError(error,'old linked preservation failed; no inference or retry')
    os.fsync(directory);os.fsync(private_directory)
    after=linked_attributes(private_directory,'current-link.private',held)
    if first['metadata'][:8]!=after['metadata'][:8]or first['target']!=after['target']or first['acl']!=after['acl']:
        raise ValueError('preserved old linked inode changed')
    return after
