"""BUG755/YKT535: host private log boundary, not a VM lifecycle command.
The caller supplies a fixed reviewed command; this wrapper neither retries nor
prints the argv/output. Existing paths, links, or unsafe parents are refused.
"""
import os
import pathlib
import stat
import subprocess
import sys


def run(log, command):
    if not isinstance(log, pathlib.Path) or not log.is_absolute() or not command:
        raise ValueError('private command rejected')
    parent = log.parent.lstat()
    if (not stat.S_ISDIR(parent.st_mode) or parent.st_uid != os.getuid()
            or stat.S_IMODE(parent.st_mode) != 0o700 or not log.name.endswith('.private.log')):
        raise ValueError('private log parent rejected')
    fd = os.open(log, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        s = os.fstat(stream.fileno())
        if not stat.S_ISREG(s.st_mode) or s.st_uid != os.getuid() or s.st_nlink != 1 or stat.S_IMODE(s.st_mode) != 0o600:
            raise ValueError('private log inode rejected')
        result = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=stream, stderr=stream)
        stream.flush()
        os.fsync(stream.fileno())
    return result.returncode


if __name__ == '__main__':
    if len(sys.argv) < 4 or sys.argv[2] != '--':
        raise SystemExit('fixed private log and reviewed command required')
    code = run(pathlib.Path(sys.argv[1]), sys.argv[3:])
    print(f'PG471_PRIVATE_COMMAND actualExit={code} rawOutputLogged=false retry0=true')
    raise SystemExit(code)
