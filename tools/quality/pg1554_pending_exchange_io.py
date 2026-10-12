"""Fixed no-epoch partial current exchange IO; caller proves authority and state."""
import os
import stat
import ctypes
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'vm/050_s1'))
from pg1088_cold_exchange_io import _native,linked_attributes
__all__=['linked_attributes','exchange','move_old_link']

def exchange(directory,stage,call=_native):
    if type(directory)is not int or directory<0 or stage!='pg1551-current.part'or type(stage)is not str or not callable(call):raise ValueError('fixed partial exchange arguments required')
    if not stat.S_ISDIR(os.fstat(directory).st_mode):raise ValueError('held current directory required')
    value,error=call(directory,stage)
    if value!=0:raise OSError(error,'partial exchange failed; no inference/retry')

def _native_move(directory,private):
    libc=ctypes.CDLL(None,use_errno=True);rename=libc.renameat2
    rename.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint];rename.restype=ctypes.c_int;ctypes.set_errno(0)
    value=rename(directory,b'pg1551-current.part',private,b'current-link.private',1)
    return value,ctypes.get_errno()

def move_old_link(directory,private,held,call=_native_move):
    if any(type(fd)is not int or fd<0 for fd in [directory,private,held])or not callable(call):raise ValueError('held partial link directories required')
    if any(not stat.S_ISDIR(os.fstat(fd).st_mode)for fd in [directory,private]):raise ValueError('held directory type required')
    first=linked_attributes(directory,'pg1551-current.part',held)
    if first['target']!='/opt/schubert-nk/releases/0.1.0-PG1292':raise ValueError('old signed source link required')
    try:os.stat('current-link.private',dir_fd=private,follow_symlinks=False)
    except FileNotFoundError:pass
    else:raise FileExistsError('new-only private link destination required')
    if os.fstat(directory).st_dev!=os.fstat(private).st_dev:raise ValueError('same filesystem link preservation required')
    value,error=call(directory,private)
    if value!=0:raise OSError(error,'partial old-link move failed; no inference/retry')
    os.fsync(directory);os.fsync(private)
    after=linked_attributes(private,'current-link.private',held)
    if first['metadata'][:8]!=after['metadata'][:8]or first['target']!=after['target']or first['acl']!=after['acl']:raise ValueError('preserved same old inode changed')
    return after
