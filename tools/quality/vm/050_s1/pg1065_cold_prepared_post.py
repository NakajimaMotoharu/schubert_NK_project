"""Independent readonly post: actual prepared layout, all resource0 and old original bytes."""
import ast
import datetime
import hashlib
import json
import os
import subprocess
from pg1041_cold_policy_diagnostic import P,W

GUEST=r'''
import pathlib,os,hashlib,json,ast,types,traceback,subprocess
os.umask(0o077);assert os.geteuid()==0
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cbca8738-3b24-4090-b77c-bf029677cdd6'
raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1062-cold-tools-v1/pg1062_cold_refs.py').read_bytes()
assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
nodes=[]
for n in ast.parse(raw).body:
 if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef)):nodes.append(n)
 elif isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)for t in n.targets):
  if {t.id for t in n.targets}<={'CHECKSUM_HASH','CONTRACT_SOURCE','LOCK_SOURCE','MANIFEST_SIZE','BOOT','SOURCE','BASELINE_HASH','BOM','PIN_HASH','SIG_HASH','CONFIG_FIELDS','RELEASE','FIELDS'}:nodes.append(n)
env={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'frozen1062','exec'),env)
contract=types.ModuleType('contract');exec(env['CONTRACT_SOURCE'],contract.__dict__);env['contract']=contract
env['owned_flocks']=lambda lines,m,pid:contract.free_flocks(lines,m)if pid==0 else (_ for _ in()).throw(ValueError('post owner must0'))
env['OWNER_PID']=0;env['OWNER_BACKEND']=0;env['PREPARED']=True
env['old']=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg989-bootstrap-post-v4/after.private.json').read_bytes())
save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1062-cold-prepared-v1')
before_raw=(save/'before.private.json').read_bytes();after_raw=(save/'after.private.json').read_bytes()
before=json.loads(before_raw);after=json.loads(after_raw)
try:
 assert all(not pathlib.Path('/proc',str(pid)).exists()for pid in (5463,5489,7427))
 first=env['snapshot']();second=env['snapshot']();assert first==second==before==after['snapshot']
 runtime=env['runtime_namespaces']();assert runtime==env['runtime_namespaces']()==after['runtime']
 env['controls']()
 options=env['command'](['findmnt','--target',str(env['RELEASE']),'--noheadings','--output','VFS-OPTIONS'],4096).decode().strip().split(',')
 assert 'ro'in options and 'rw'not in options
 completion=(save/'complete.private.txt').read_bytes()
 assert b'allScopesReturnedNormally=true' in completion and b'originalRetiredOrAuthorityIssued=false' in completion
 print(json.dumps({'run':'PG1065-cold-prepared-post-v1','actualExit':0,'source':env['SOURCE'],'boot':env['BOOT'],
  'sameAll24OriginalsTwice':True,'exactPreparedNamespaceTwice':True,'allClientsAdvisoryAndFlocks0':True,'oldActorsGone':True,
  'payloadHostReadonly':True,'startupEpochAndRequestsEmpty':True,'javaCompletionReceiptNormal':True,
  'beforePrivateSha256':hashlib.sha256(before_raw).hexdigest(),'afterPrivateSha256':hashlib.sha256(after_raw).hexdigest(),
  'completedReceiptSha256':hashlib.sha256(completion).hexdigest(),'dataOnly':True,'formalAccepted':False}))
except Exception as failure:
 print(json.dumps({'run':'PG1065-cold-prepared-post-v1','type':type(failure).__name__,
  'frames':[{'function':x.name,'line':x.lineno,'file':pathlib.Path(x.filename).name}for x in traceback.extract_tb(failure.__traceback__)][-5:],
  'dataOnly':True,'formalAccepted':False}))
 raise SystemExit(1)
'''


def main():
    os.umask(0o077);out=W/'pg1065-cold-prepared-post-v1';out.mkdir(mode=0o700)
    frozen=json.loads((W/'pg1063-cold-preparation-frozen-v2.safe.json').read_bytes())
    child=W/'pg1062-cold-tools-v1/pg1062_cold_refs.py'
    if frozen['actualExit']!=0 or hashlib.sha256(child.read_bytes()).hexdigest()!=frozen['fileHashes'][child.name]:
        raise ValueError('frozen new source required')
    result=json.loads((W/'pg1064-prepare-v1.safe.json').read_bytes())
    if result['actualExit']!=0 or not result['fullColdPreparationAccepted']:
        raise ValueError('actual normal new preparation required')
    raw=('SOURCE_SHA='+repr(frozen['fileHashes'][child.name])+'\n'+GUEST).encode()
    with(out/'guest-script.private.py').open('xb')as f:f.write(raw)
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes',
         '-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    start=datetime.datetime.now(datetime.timezone.utc)
    r=subprocess.run(ssh,input=raw,capture_output=True,timeout=60)
    with(out/'result.private.log').open('xb')as f:f.write(r.stdout+r.stderr);f.flush();os.fsync(f.fileno())
    value={'run':'PG1065-cold-prepared-post-v1','operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
           'preparedOperatorSource':frozen['operatorSource'],'actualExit':r.returncode,'startedUTC':start.isoformat(),
           'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scriptSha256':hashlib.sha256(raw).hexdigest(),
           'logSha256':hashlib.sha256(r.stdout+r.stderr).hexdigest(),'dataOnly':True,'formalAccepted':False}
    if r.returncode==0:value['observed']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(value));raise SystemExit(r.returncode)


if __name__=='__main__':
    main()
