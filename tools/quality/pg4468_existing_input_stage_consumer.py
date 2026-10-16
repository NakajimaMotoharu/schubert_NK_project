"""Consume existing exact transferred files, never replay upload or original stage."""
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
import pg4462_failed_unused_dispatch as dispatch
from pg4434_current_candidate_admission_read import authenticate_host
from pg1446_current_cold_stage import W, P, SSH
from pg1674_critical_management_gate import management_gate


def main():
    original = json.loads((W/'pg4462-stage-v1.safe.json').read_bytes())
    if original['actualExit'] != 1 or original['privateLogSha256'] != '7eb8742026df4f1617ae0fb8165b230a755457602114a481fb4cb5a5e5d0e15f':
        raise ValueError('actual original pre-root-stage refusal required')
    frozen = json.loads((W/'pg4460-frozen-v1.safe.json').read_bytes())
    if frozen['actualExit'] != 0 or frozen['completeGraphQualified'] is not True: raise ValueError('same frozen142 required')
    tools = P/(dispatch.role.TOOLS+'.tar')
    inputs = {
        '/home/ubuntu/pg4462-fixed-stage-v1/'+tools.name:hashlib.sha256(tools.read_bytes()).hexdigest(),
        dispatch.role.REMOTE+'/'+dispatch.role.ARCHIVE:hashlib.sha256((P/dispatch.role.ARCHIVE).read_bytes()).hexdigest(),
        dispatch.role.REMOTE+'/pg4432-manifest-v1.sig':hashlib.sha256((P/'pg4432-manifest-v1.sig').read_bytes()).hexdigest(),
        dispatch.role.REMOTE+'/bundle.safe.json':hashlib.sha256((dispatch.TARGET/'bundle.safe.json').read_bytes()).hexdigest()}
    prelude = '''
import os,stat,hashlib
from pathlib import Path
for name,digest in INPUTS.items():
 p=Path(name);s=p.lstat();d=p.parent.lstat()
 assert stat.S_ISREG(s.st_mode)and s.st_uid==1000 and s.st_nlink==1 and not p.is_symlink()
 assert stat.S_ISDIR(d.st_mode)and d.st_uid==1000 and stat.S_IMODE(d.st_mode)==0o700
 assert stat.S_IMODE(s.st_mode)in (0o400,0o600)and not os.listxattr(p)and not os.listxattr(p.parent)
 assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
assert not os.path.lexists(GUEST)
'''
    raw = 'INPUTS='+repr(inputs)+'\nGUEST='+repr(dispatch.GUEST)+'\n'+prelude
    raw += '\nDIGEST='+repr(inputs[next(iter(inputs))])+'\nFILES='+repr(frozen['fileHashes'])+'\n'+dispatch.stage_source()
    if check(raw,'<existing exact input new-only stage consumer>'): raise ValueError('whole emitted static0')
    authenticate_host(); os.umask(0o077); out=W/'pg4468-existing-input-stage-v1'; out.mkdir(mode=0o700)
    (out/'payload.private.py').write_text(raw)
    with management_gate(P/'current-management-critical.lock'):
        result=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=120)
    (out/'observer.private.log').write_bytes(result.stdout+result.stderr)
    value={'actualExit':result.returncode,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),
        'frozenFiles':142,'originalStageActualExit':1,'originalStageReplayed':False,'filesRetransferred':False,
        'candidateSource':dispatch.role.SOURCE,'currentSource':dispatch.role.CURRENT,'guestTools':dispatch.GUEST,
        'candidatePlaced':False,'formalAccepted':False}
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
