"""Bounded public delta scan since recovery savepoint; never runtime/private input."""
import datetime
import hashlib
import json
import os
import subprocess
from pathlib import Path

import pg6908_public_delta_scan as scan
from host_tool_invocation import capture, verify
import public_delta_tombstone_contract as tombstone

BEFORE='4f999670a835e8500dfecee19b456977185eaa69'
OUT=scan.BASE/'PG6990-recovery-public-delta-v1'
TOMBSTONES=frozenset()
COMMON={
 'program/characterization/src/main/java/dev/codex/schubert/characterization/GateCli.java',
 'program/characterization/tests/java/dev/codex/schubert/characterization/GateCliTest.java'}


def allowed(path):
    return ('/private' not in path and not path.endswith('.private.log')
            and (path.startswith(('tools/quality/','documents/','evidence/01_PT/','src/')) or path in COMMON))


def main():
    invocation=capture(Path(__file__))
    names=scan.paths(subprocess.check_output(['git','diff','--name-only','-z',BEFORE,'--'],cwd=scan.ROOT))
    names.update(scan.paths(subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=scan.ROOT)))
    if TOMBSTONES:
        deleted=scan.paths(subprocess.check_output(['git','diff','--no-renames','--diff-filter=D','--name-only','-z',BEFORE,'--'],cwd=scan.ROOT))
        tombstone.verify_scope(TOMBSTONES,deleted)
        names.update(TOMBSTONES)
    own=OUT.relative_to(scan.ROOT).as_posix()+'/'
    names={p for p in names if not p.startswith(own)}
    rows,findings=[],[]
    for name in sorted(names):
        path=scan.ROOT/name
        if not allowed(name) or path.is_symlink():
            raise ValueError('only exact declared public text scope, unknown input never clean')
        if path.is_file():
            raw=path.read_bytes()
            origin='CURRENT_PUBLIC_TEXT'
        elif name in TOMBSTONES and not path.exists():
            ref=BEFORE+':'+name
            header=subprocess.check_output(['git','ls-tree',BEFORE,'--',name],cwd=scan.ROOT,text=True).split()
            if len(header)!=4:
                raise ValueError('unambiguous tracked original file required')
            size=int(subprocess.check_output(['git','cat-file','-s',ref],cwd=scan.ROOT,text=True))
            tombstone.verify_blob(header[0],header[1],size)
            raw=subprocess.check_output(['git','show',ref],cwd=scan.ROOT)
            if len(raw)!=size:
                raise ValueError('original Git blob size differs')
            origin='DELETED_CURRENT_PATH_ORIGINAL_GIT_BLOB_PRESERVED'
        else:
            raise ValueError('unknown missing public input is not a known deletion')
        if b'\0' in raw:
            raise ValueError('public text only, no binary classification fallback')
        raw.decode('utf-8')
        rows.append(dict(path=name,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),origin=origin,
                         originalGitRef=BEFORE+':'+name if name in TOMBSTONES else None))
        findings.extend(dict(path=name,**f) for f in scan.inspect_bytes(raw))
    if not rows:raise ValueError('nonempty actual delta')
    value=dict(actualExit=1 if findings else 0,before=BEFORE,
               head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=scan.ROOT,text=True).strip(),
               timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
               command=invocation['actualPythonCommand'],invocation=invocation,toolSha256=scan.sha(Path(__file__)),
               files=rows,findings=findings,rules=list(scan.RULES),matchedValuesSaved=False,
               scope='DECLARED_RECOVERY_PUBLIC_TEXT_DELTA_THREE_FORMAT_PATTERNS_NOT_ALL_SECRETS_OR_RUNTIME',
               preciseCommonScope=sorted(COMMON),selfOutputOnlyExcluded=own,newPt=0,vmActions=0,formalUpdated=False)
    value['explicitGitTombstones']=sorted(TOMBSTONES)
    verify(invocation)
    os.umask(0o077);OUT.mkdir()
    with (OUT/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=value['actualExit'],publicFiles=len(rows),findings=len(findings),manifestSha256=scan.sha(OUT/'manifest.json'))))
    raise SystemExit(value['actualExit'])


if __name__=='__main__':main()
