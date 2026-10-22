"""Bounded public delta scan since recovery savepoint; never runtime/private input."""
import datetime
import json
import os
import subprocess
from pathlib import Path

import pg6908_public_delta_scan as scan

BEFORE='4f999670a835e8500dfecee19b456977185eaa69'
OUT=scan.BASE/'PG6990-recovery-public-delta-v1'
COMMON={
 'program/characterization/src/main/java/dev/codex/schubert/characterization/GateCli.java',
 'program/characterization/tests/java/dev/codex/schubert/characterization/GateCliTest.java'}


def allowed(path):
    return ('/private' not in path and not path.endswith('.private.log')
            and (path.startswith(('tools/quality/','documents/','evidence/01_PT/','src/')) or path in COMMON))


def main():
    names=scan.paths(subprocess.check_output(['git','diff','--name-only','-z',BEFORE,'--'],cwd=scan.ROOT))
    names.update(scan.paths(subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=scan.ROOT)))
    own=OUT.relative_to(scan.ROOT).as_posix()+'/'
    names={p for p in names if not p.startswith(own)}
    rows,findings=[],[]
    for name in sorted(names):
        path=scan.ROOT/name
        if not allowed(name) or path.is_symlink() or not path.is_file() or b'\0' in path.read_bytes():
            raise ValueError('only exact declared public text scope, unknown input never clean')
        raw=path.read_bytes()
        rows.append(dict(path=name,sha256=scan.sha(path),bytes=len(raw)))
        findings.extend(dict(path=name,**f) for f in scan.inspect_bytes(raw))
    if not rows:raise ValueError('nonempty actual delta')
    value=dict(actualExit=1 if findings else 0,before=BEFORE,
               head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=scan.ROOT,text=True).strip(),
               timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
               command='python3 -B tools/quality/pg6990_recovery_public_scan.py',toolSha256=scan.sha(Path(__file__)),
               files=rows,findings=findings,rules=list(scan.RULES),matchedValuesSaved=False,
               scope='DECLARED_RECOVERY_PUBLIC_TEXT_DELTA_THREE_FORMAT_PATTERNS_NOT_ALL_SECRETS_OR_RUNTIME',
               preciseCommonScope=sorted(COMMON),selfOutputOnlyExcluded=own,newPt=0,vmActions=0,formalUpdated=False)
    os.umask(0o077);OUT.mkdir()
    with (OUT/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=value['actualExit'],publicFiles=len(rows),findings=len(findings),manifestSha256=scan.sha(OUT/'manifest.json'))))
    raise SystemExit(value['actualExit'])


if __name__=='__main__':main()
