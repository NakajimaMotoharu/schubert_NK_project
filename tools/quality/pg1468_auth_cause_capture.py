"""Read bounded synthetic diagnostic; export categories only, never raw SQL."""
import hashlib
import json
import os
from pathlib import Path
import stat
import time


def stable(st):
    return (st.st_dev,st.st_ino,st.st_mode,st.st_uid,st.st_gid,st.st_nlink,
            st.st_size,st.st_mtime_ns,st.st_ctime_ns)


def main():
    os.umask(0o077)
    out=Path('/home/mini/schubert-nk-pgpt/runs/PG1468-auth-cause-v1');out.mkdir(mode=0o700)
    files=list(Path('/tmp').glob('auth-diagnostic-*.private.log'))
    assert len(files)==1
    p=files[0];m=p.lstat()
    assert stat.S_ISREG(m.st_mode) and m.st_uid==os.getuid() and m.st_nlink==1
    assert stat.S_IMODE(m.st_mode)==0o600 and 0<m.st_size<1048576
    b=p.read_bytes();assert stable(p.lstat())==stable(m)
    counts={};statements=[];text=b.decode()
    lines=text.splitlines()
    for i,line in enumerate(lines):
        for key in ['canceling statement due to lock timeout',
                    'canceling statement due to statement timeout','deadlock detected']:
            if key in line:
                counts[key]=counts.get(key,0)+1
                # Categorize fixed schema/query shape; don't export parameters.
                following=next((s for s in lines[i+1:i+8] if 'STATEMENT:' in s),'')
                statements.append({'category':key,
                    'userRowForUpdate': 'from schubert.app_users where username_key=' in following
                                        and 'for update' in following.lower()})
    with(out/'auth-database.private.log').open('xb')as f:
        f.write(b);f.flush();os.fsync(f.fileno())
    result={'run':'PG1468-auth-cause-v1','actualExit':0,'rawExported':False,
            'privateLogSha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),
            'categories':counts,'statements':statements,
            'privateLogRoot':'PG1468-auth-cause-v1','formalAccepted':False}
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(result,sort_keys=True));return 0


if __name__=='__main__':raise SystemExit(main())
