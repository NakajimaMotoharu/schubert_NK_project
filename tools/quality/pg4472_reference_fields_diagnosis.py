"""Exact sealed show definition and independent requested/returned keys; no operations."""
import ast
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
import pg4470_inspect_unknown_read as previous
from pg4438_failed_current_canonical_view import PARENT_FIELDS
from pg4434_current_candidate_admission_read import authenticate_host
from pg1446_current_cold_stage import SSH, W


def payload():
    tree=ast.parse(previous.GUEST);last=tree.body[-1]
    if not isinstance(last,ast.Expr):raise ValueError('one original final readonly boundary')
    head=''.join(previous.GUEST.splitlines(keepends=True)[:last.lineno-1])
    body=r'''
sealed=Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes()
assert hashlib.sha256(sealed).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7'
module=ast.parse(sealed)
definition=next(ast.get_source_segment(sealed.decode(),n)for n in module.body if isinstance(n,ast.FunctionDef)and n.name=='show')
constants=[ast.get_source_segment(sealed.decode(),n)for n in module.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='FIELDS'for t in n.targets)]
before=Path('/var/lib/pgpt-s1-preservation/pg4440-failed-full-image-diagnosis-v1/canonical-first11.private.json').read_bytes()
assert hashlib.sha256(before).hexdigest()=='8e000cbabdde5c903c5c6b48e875fe4b104ee54520e0b19a233a959c510d00ff'
unit_keys={}
for name in json.loads(before)['units']:
 r=subprocess.run(['systemctl','show',name,'--property='+','.join(REQUESTED)],capture_output=True,timeout=10);assert r.returncode==0
 keys=[line.split(b'=',1)[0].decode('ascii')for line in r.stdout.splitlines()]
 unit_keys[name]={'returnedCount':len(keys),'missing':sorted(set(REQUESTED)-set(keys)),'extra':sorted(set(keys)-set(REQUESTED))}
print(json.dumps({'actualExit':0,'actors':actors,'peers':peers,'flocks':locks,'showDefinition':definition,'sealedFieldsDefinitions':constants,
 'allUnitRequestedReturnedKeys':unit_keys,'candidateReleaseExists':os.path.lexists('/opt/schubert-nk/releases/0.1.0-PG4432'),
 'signalsOrBusinessOperations':0,'oldScopesNormal':False,'formalAccepted':False}))
'''
    raw='import ast\nREQUESTED='+repr(PARENT_FIELDS)+'\n'+head+body
    if check(raw,'<sealed exact field diagnosis>'):raise ValueError('all emitted static0')
    return raw


def main():
    raw=payload();authenticate_host();os.umask(0o077);out=W/'pg4472-reference-fields-diagnosis-v1';out.mkdir(mode=0o700)
    (out/'payload.private.py').write_text(raw)
    result=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=60)
    (out/'observer.private.log').write_bytes(result.stdout+result.stderr)
    value={'actualExit':result.returncode,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'signalsOrBusinessOperations':0,'formalAccepted':False}
    if result.returncode==0:value['result']=json.loads(result.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
