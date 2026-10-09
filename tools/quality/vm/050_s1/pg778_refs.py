"""SSC235 continuous ten Unit Ref + held directories, same actual Java M/A/DB owner."""
import hashlib
import os
from pathlib import Path
import sys
import time
from pg778_owned import holder,require
from pg777_reference_capability import CaptureReferences


def main():
    require(os.geteuid()==0 and len(sys.argv)==3 and sys.argv[1]in ('verify','recover')and sys.argv[2].isdigit())
    root=Path(__file__).resolve().parent
    expected=__import__('json').loads((root/'payload-sha256.json').read_text())
    for name in ('pg778_refs.py','pg778_owned.py','pg777_reference_capability.py'):
        require(hashlib.sha256((root/name).read_bytes()).hexdigest()==expected[name])
    owner=holder();fds=[];refs=None
    try:
        refs=CaptureReferences();refs.__enter__()
        for path in ('/run/schubert-nk/startup','/run/schubert-nk/backup-request','/run/schubert-nk/cleanup-request','/run/schubert-nk/expiry-request','/var/lib/schubert-nk/maintenance','/srv/schubert-nk/backup','/srv/schubert-nk/data/transfer','/srv/schubert-nk/data/assets','/etc/schubert-nk/credentials','/etc/schubert-nk/release-approval'):
            fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);fds.append((path,fd,os.fstat(fd).st_dev,os.fstat(fd).st_ino))
        require(owner==holder());print('REF_READY',flush=True)
        for line in sys.stdin.buffer:
            require(line==b'release\n'and owner==holder())
            for path,fd,dev,ino in fds:
                actual=os.stat(path,follow_symlinks=False);held=os.fstat(fd)
                require((actual.st_dev,actual.st_ino)==(held.st_dev,held.st_ino)==(dev,ino))
            for _,fd,_,_ in reversed(fds):os.close(fd)
            fds=[];refs.__exit__(None,None,None);refs=None
            require(owner==holder());print('REF_RELEASED',flush=True);return
        raise ValueError('owned reference channel ended')
    except BaseException as failure:
        # All genuinely held objects stay referenced here; never claim a failed close returned.
        print('REF_FAILED',flush=True);print('PG778_REF_UNKNOWN type='+type(failure).__name__+' heldScopeNotInferred=false',file=sys.stderr,flush=True)
        while True:time.sleep(1)


if __name__=='__main__':main()
