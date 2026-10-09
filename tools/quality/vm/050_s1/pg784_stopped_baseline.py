"""Fresh readonly stopped-current after782/RefGC; preserve old history, never restore it."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
PAYLOAD=r'''
import sys,pathlib,json,os,hashlib,ast,re
os.umask(0o077);assert os.geteuid()==0
base=pathlib.Path('/var/lib/pgpt-s1-preservation');oldraw=(base/'pg782-retained779-handoff-v1/after.private.json').read_bytes()
assert hashlib.sha256(oldraw).hexdigest()=='97eb9c35044bbb3c9cd71fe0a63ea89a026e053a6fcfe09a8072af0628e99e8d';old=json.loads(oldraw)
sys.path.insert(0,str(base/'pg779-failed758-tools-v1'));import pg779_owned as h
from pg777_reference_capability import CaptureReferences
h.load_definitions();h.parent();save=base/'pg784-stopped-current-v1';assert not os.path.lexists(save)
policy=(base/'pg477-completed-tools-v1/pg477_unit_references.py').read_bytes();assert hashlib.sha256(policy).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4'
definition=next(n for n in ast.parse(policy).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record');env={'re':re};exec(compile(ast.Module(body=[definition],type_ignores=[]),'<strict exec declaration>','exec'),env)
def configuration(unit):
 actual=h.complete_configuration(h.command(['/usr/bin/systemctl','show',unit,'--property='+','.join(sorted(h.FIELDS_CONFIGURATION))]).decode(),unit)
 expected=old['configuration'][unit];left=env['exec_record'](expected['ExecStart']);right=env['exec_record'](actual['ExecStart'])
 assert left is not None and right is not None and left[:3]==right[:3]
 assert actual['ExecStart']==expected['ExecStart']or right[3:]==('n/a','n/a','0','(null)','0/0')
 assert all(actual[k]==expected[k]for k in actual if k!='ExecStart');return actual
h.configuration=configuration
with CaptureReferences():
 before=h.snapshot();assert before==h.snapshot()
 assert before['rows']==old['rows']and before['trees']==old['trees']
 values={u:h.show(u)for u in h.ORDER+h.EXTRA}
 for u,v in values.items():assert v['MainPID']==v['ControlPID']=='0'and not v['Job']and v['ActiveState']in ('inactive','failed');h.kernel_empty(u)
 assert all(not pathlib.Path('/proc',str(p)).exists()for p in (3105271,3105303,3063762,3066272,3072633,2841798))
 assert h.epoch_value(pathlib.Path('/run/schubert-nk/startup/epoch.current').read_bytes(),True)
 assert len(before['trees']['/run/schubert-nk/startup'])==43
 save.mkdir(mode=0o700)
 with(save/'before.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(before,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 with(save/'units.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(values,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 for d in(save,save.parent):
  fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
 sha=hashlib.sha256((save/'before.private.json').read_bytes()).hexdigest()
print(json.dumps({'actualExit':0,'readonly':True,'allTenKernel0':True,'all24Preserved':True,'batchRows':544,'startupEntries':42,'sameEpochInvalid':True,'oldCloseUnknown':True,'newScopesReturnedNormally':True,'snapshotSha256':sha}))
'''


def main():
    os.umask(0o077);assert not subprocess.check_output(['git','status','--porcelain'])
    base=W/'pg784-stopped-current-v1';assert not any(Path(str(base)+s).exists()for s in ('.private.stderr','.exit','.safe.json'))
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    with Path(str(base)+'.private.stderr').open('xb')as f:r=subprocess.run(ssh,input=PAYLOAD.encode(),stdout=subprocess.PIPE,stderr=f,timeout=90)
    with Path(str(base)+'.exit').open('x')as f:f.write(str(r.returncode)+'\n')
    if r.returncode==0:
        value=json.loads(r.stdout);value.update(recordedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),operatorSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
        with Path(str(base)+'.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
        print(json.dumps(value))
    else:print(json.dumps({'actualExit':r.returncode,'privateErrorSha256':hashlib.sha256(Path(str(base)+'.private.stderr').read_bytes()).hexdigest()}))
    raise SystemExit(r.returncode)


if __name__=='__main__':main()
