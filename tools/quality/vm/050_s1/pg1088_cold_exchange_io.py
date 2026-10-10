"""SSC250 fixed current/sibling exchange, no fallback/retry or automatic authority.

Caller owns M/A/RODB/Refs/original and proves fd/namespace/source before real use.
This IO primitive alone grants neither runtime admission nor publication rights.
"""
import ctypes
import os
import stat


def _identity(value):
    # SSC250's complete nine-field contract excludes access time: readlink
    # itself may update it under relatime. Never exclude mtime/ctime or ACL.
    return (value.st_dev,value.st_ino,value.st_uid,value.st_gid,value.st_mode,value.st_nlink,
            value.st_size,value.st_mtime_ns,value.st_ctime_ns)


def _native(directory,stage):
    libc=ctypes.CDLL(None,use_errno=True)
    function=libc.renameat2
    function.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint]
    function.restype=ctypes.c_int
    ctypes.set_errno(0)
    result=function(directory,stage.encode('ascii'),directory,b'current',2)
    return result,ctypes.get_errno()


def exchange(directory,stage,call=_native):
    if (type(directory)is not int or directory<0 or stage!='pg1088-current.part'
        or type(stage)is not str or not callable(call)):
        raise ValueError('fixed exchange arguments refused')
    if not stat.S_ISDIR(os.fstat(directory).st_mode):raise ValueError('fixed exchange directory refused')
    result,code=call(directory,stage)
    if result!=0:raise OSError(code,'fixed exchange failed; state not inferred; no retry')


def linked_attributes(directory,name,held):
    """Linked path + O_PATH inode/target, twice; no O_PATH xattr fallback."""
    if type(name)is not str or not name or '/'in name or name in ('.','..'):
        raise ValueError('linked alias refused')
    first=os.fstat(held)
    if not stat.S_ISLNK(first.st_mode)or first.st_nlink!=1:raise ValueError('held link type/count refused')
    linked=os.stat(name,dir_fd=directory,follow_symlinks=False)
    if _identity(first)!=_identity(linked):raise ValueError('held/linked identity refused')
    target=os.readlink('',dir_fd=held)
    if target!=os.readlink(name,dir_fd=directory):raise ValueError('held/linked target refused')
    # Use the held directory spelling only after verifying its actual FD/link.
    # No pathname substitution may supply the expected identity.
    path='/proc/self/fd/'+str(directory)+'/'+name
    attrs=tuple(os.listxattr(path,follow_symlinks=False))
    last=os.fstat(held)
    if _identity(first)!=_identity(last) or _identity(last)!=_identity(os.stat(name,dir_fd=directory,follow_symlinks=False)):
        raise ValueError('held/linked identity changed')
    if target!=os.readlink('',dir_fd=held)or target!=os.readlink(name,dir_fd=directory):
        raise ValueError('held/linked target changed')
    return {'metadata':[last.st_dev,last.st_ino,last.st_uid,last.st_gid,last.st_mode,last.st_nlink,
                        last.st_size,last.st_mtime_ns,last.st_ctime_ns],
            'target':target,'sha256':None,'acl':list(attrs)}
