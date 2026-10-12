"""Minimal SS metadata9 fix in a new profile; frozen failed Unit helper unmodified."""
import inspect
import pg1877_unit_exchange_contract as prior


def source():
    raw=inspect.getsource(prior)
    old='require(old==named and'
    if raw.count(old)!=1:raise ValueError('one actual preserved old inode guard required')
    raw=raw.replace(old,'require(metadata9(old)==metadata9(named) and')
    definition='''
def metadata9(value):
    return (value.st_dev,value.st_ino,value.st_uid,value.st_gid,value.st_mode,value.st_nlink,value.st_size,value.st_mtime_ns,value.st_ctime_ns)

'''
    if raw.count('class UnitExchange:')!=1:raise ValueError('one actual whole Unit class required')
    return raw.replace('class UnitExchange:',definition+'class UnitExchange:')
