"""Independent readonly final after PG549 normal code-only publish. No repeat action."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

os.umask(0o077)
R=Path(__file__).resolve().parent;T=R.parents[3]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip()
files={n:(R/n).read_bytes()for n in('pg542_current_contract.py','pg543_retirement_contract.py','pg543_runtime_readback.py','pg549_completed_contract.py','pg549_completed_refs.py')}
hashes={n:hashlib.sha256(raw).hexdigest()for n,raw in files.items()}
for mode in('verify','activate'):
    safe=json.loads((W/('pg549-'+mode+'-v5.safe.json')).read_bytes());assert safe['actualExit']==0
    for n in files:assert safe['toolHashes'][n]==hashes[n]
payload='import sys,types\n'
for name in('pg542_current_contract.py','pg543_retirement_contract.py','pg543_runtime_readback.py','pg549_completed_contract.py'):
    payload+='m=types.ModuleType('+repr(name[:-3])+');m.__file__='+repr(name)+';sys.modules[m.__name__]=m;exec(compile('+repr(files[name].decode())+','+repr(name)+",'exec'),m.__dict__)\n"
payload+='REFS='+repr(files['pg549_completed_refs.py'].decode())+'\nHASHES='+repr(hashes)+'\n'
payload+=r'''
import ast,os,re,json,hashlib,pathlib,stat,subprocess,dbus
from pathlib import Path
from pg543_runtime_readback import load,BOOT,RUNTIME
from pg549_completed_contract import EPOCH,APPROVAL,NEXT,DIGEST,NEW_APPROVAL,changed_only,require
require(os.geteuid()==0 and Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
base=Path('/var/lib/pgpt-s1-preservation');proof=base/'pg549-completed-activate-v5';verify=base/'pg549-completed-verify-v5'
require({p.name for p in proof.iterdir()}=={'before.private.json','after.private.json','refs-prepare.private.log','old-approval.private','old-current.private','old-epoch.private','complete.private'})
require({p.name for p in verify.iterdir()}=={'before.private.json','after.private.json','refs-prepare.private.log','complete.private'})
require((verify/'before.private.json').read_bytes()==(verify/'after.private.json').read_bytes())
for mode,p in [('verify',verify),('activate',proof)]:
    require((p/'complete.private').read_bytes()==('completedCurrentVerified=true\nmode='+mode+'\nallNewScopesReturnedNormally=true\nrequestsUnchanged=true\ndatabaseUpdates0=true\nstarts0=true\n').encode())
    require((p/'refs-prepare.private.log').read_bytes()==b'')
for name,sha in HASHES.items():require(hashlib.sha256((base/'pg549-completed-tools-v5'/name).read_bytes()).hexdigest()==sha)
boundary=json.loads((base/'pg543-runtime-retirement-v2/boundaries.private.json').read_bytes())
env,baseline,_,_,_,captured=load(post=True,caddy_before=boundary['caddyExecStartPre'])
def owner():require(os.geteuid()==0)
def connection():
    sql="select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;"
    require(env['command'](['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],4096).splitlines()==[b'0',b'0'])
paths=[Path(EPOCH).parent,Path(APPROVAL).parent,proof,verify]
fds=[os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)for p in paths]
original=[os.fstat(fd)for fd in fds]
def directories():
    for p,fd,old in zip(paths,fds,original):
        def identity(s):return(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink)
        require(identity(p.lstat())==identity(os.fstat(fd))==identity(old)and'system.posix_acl_access'not in os.listxattr(p))
main=next(n for n in ast.parse(REFS).body if isinstance(n,ast.FunctionDef)and n.name=='main')
nodes=[n for n in main.body if isinstance(n,ast.FunctionDef)and n.name in('file','extras','snapshot')];require(len(nodes)==3)
exec(compile(ast.Module(body=nodes,type_ignores=[]),'<pinned independent raw capture>','exec'),globals())
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
for unit in env['UNITS']:manager.RefUnit(unit);refs.append(unit)
before=json.loads((proof/'before.private.json').read_bytes());after=json.loads((proof/'after.private.json').read_bytes())
old_epoch=env['strict'](proof/'old-epoch.private',0o600,4096);new_epoch=env['strict'](Path(EPOCH),0o600,4096)
changed_only(before,after,old_epoch,new_epoch);require(snapshot()==after==snapshot())
require(Path('/opt/schubert-nk/current').readlink()==Path(NEXT)and env['strict'](Path(APPROVAL),0o400,192)==NEW_APPROVAL)
r=Path(NEXT);raw=(r/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(raw).hexdigest()==DIGEST)
data=json.loads(raw);require(data['source']['commit']=='969d8ded10c0bf5841d9e3a5c531e922caf4a24a'and len(data['artifacts'])==187 and len(data['migrations'])==29 and data['versions']['schema']=='028')
for a in data['artifacts']:
    p=r/a['path'];require(p.stat().st_size==a['size']and hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256'])
env['command'](['/usr/bin/openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(r/'RELEASE-MANIFEST.json'),'-sigfile',str(base/'pg548-manifest.sig')],4096)
options=env['command'](['/usr/bin/findmnt','--noheadings','--output','OPTIONS','--mountpoint',NEXT],4096).decode().strip().split(',');require('ro'in options)
connection();require(snapshot()==after)
for unit in reversed(refs):manager.UnrefUnit(unit)
bus.close()
for fd in reversed(fds):os.close(fd)
connection()
for name in('maintenance.lock','startup-admission.lock'):
    p=Path('/run/schubert-nk')/name;s=p.lstat()
    for line in Path('/proc/locks').read_text().splitlines():
        a=line.split()
        if len(a)>=8 and a[1]=='FLOCK':
            dev=a[5].split(':');require((int(dev[0],16),int(dev[1],16),int(dev[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))
def proof_hashes(p):return {x.name:{'sha256':hashlib.sha256(x.read_bytes()).hexdigest(),'bytes':x.stat().st_size}for x in p.iterdir()}
print(json.dumps({'run':'PG552-completed-publish-final-v1','actualExit':0,'productionSource':data['source']['commit'],'manifestSha256':DIGEST,'whole187Verified':True,'schema028':True,'old24Tables462Preserved':True,'oldDONEOriginalsBackupNative9Preserved':True,'newFreshInvalidSameActivation':True,'normalVerifyAndActivate':True,'independentWholeAfterUnchangedTwice':True,'metadataReferencesNormallyClosed':True,'allOwnerPeerAdvisoryFlock0':True,'candidateReadonly':True,'current':NEXT,'verifyProofs':proof_hashes(verify),'activateProofs':proof_hashes(proof),'toolHashes':HASHES,'starts0':True,'databaseUpdates0':True,'authority':False,'oldFailedScopesUNKNOWNPreserved':True,'newSourceNativeAccepted':False,'formalAccepted':False}))
'''
ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
log=W/'pg552-completed-publish-final-v1.private.log';assert not log.exists()
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
result=subprocess.run(ssh,input=payload.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with log.open('xb')as f:f.write(result.stderr);f.flush();os.fsync(f.fileno())
with(W/'pg552-completed-publish-final-v1.exit').open('x')as f:f.write(str(result.returncode)+'\n')
if result.returncode:print(json.dumps({'run':'PG552-completed-publish-final-v1','actualExit':result.returncode,'privateDiagnostic':True}));raise SystemExit(result.returncode)
safe=json.loads(result.stdout);safe.update(operatorSource=source,startedUTC=started,completedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),privateLogSha256=hashlib.sha256(log.read_bytes()).hexdigest(),helperSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
with(W/'pg552-completed-publish-final-v1.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps({k:safe[k]for k in('run','actualExit','productionSource','whole187Verified','allOwnerPeerAdvisoryFlock0','formalAccepted')}))
