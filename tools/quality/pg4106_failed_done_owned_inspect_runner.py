"""Freeze candidate once and inspect that exact payload. Recovery deliberately not exposed yet."""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
from pyflakes.api import check
from lan_server import run
import pg3428_vm_candidate_preflight_readonly as identity
from pg1446_current_cold_stage import W, P, SSH
from pg1674_critical_management_gate import management_gate
import pg4104_failed_done_owned_dispatch as candidate

SLOT = 'pg4106-failed-done-dispatch-qualification-v1'
ARTIFACT = W / (SLOT + '-artifact')


def meta(path):
    s = path.lstat()
    return (s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)


def freeze():
    ARTIFACT.mkdir(mode=0o700)
    raw = candidate.payload().encode()
    if check(raw.decode(), '<full recovery candidate>') != 0: raise ValueError('complete closure first')
    path = ARTIFACT / 'dispatch.private.py'
    with path.open('xb') as f:
        f.write(raw);f.flush();os.fsync(f.fileno())
    path.chmod(0o400)
    value = {'payloadSha256':hashlib.sha256(raw).hexdigest(),'payloadBytes':len(raw),
             'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e','stateChangingActions':0}
    (ARTIFACT/'artifact.safe.json').write_text(json.dumps(value,sort_keys=True))
    fd=os.open(ARTIFACT,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
    print(json.dumps(value));return 0


def main():
    if sys.argv[1:] not in (['freeze'],['inspect']): raise SystemExit('freeze or inspect; recovery disabled')
    os.umask(0o077)
    if sys.argv[1]=='freeze':return freeze()
    # No generated source changes are allowed between freeze and this exact inspection.
    path=ARTIFACT/'dispatch.private.py';before=meta(path)
    if not(stat.S_ISREG(before[4])and before[2]==os.geteuid()and stat.S_IMODE(before[4])==0o400 and before[5]==1 and not os.listxattr(path)):
        raise ValueError('frozen artifact envelope')
    raw=path.read_bytes();qualification=json.loads((ARTIFACT/'artifact.safe.json').read_bytes())
    if meta(path)!=before or hashlib.sha256(raw).hexdigest()!=qualification['payloadSha256']or raw!=candidate.payload().encode():
        raise ValueError('exact artifact has changed')
    out=W/(SLOT+'-inspect');out.mkdir(mode=0o700)
    p=Path('/proc/20445');forward={'ticks':int((p/'stat').read_text().rsplit(')',1)[1].split()[19]),'argvSha256':hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()}
    if forward!={'ticks':104194,'argvSha256':'fd6ff71b025aa4b485f64f9dd2289f9072ac6f78d9fc6a9c44912adf8bad097b'}:raise ValueError('forward owner changed')
    code,text=run(identity.HOST,timeout=30)
    if code!=0:raise ValueError('VM/host authentication failed')
    host=json.loads(text.strip())
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-','inspect'],input=raw,capture_output=True,timeout=300)
    (out/'stdout.private.log').write_bytes(r.stdout);(out/'stderr.private.log').write_bytes(r.stderr)
    value={'actualExit':r.returncode,'source':qualification['source'],'payloadSha256':qualification['payloadSha256'],
           'host':host,'localForward':forward,'recoveryIssued':False,'formalAccepted':False}
    if r.returncode==0:value['result']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
