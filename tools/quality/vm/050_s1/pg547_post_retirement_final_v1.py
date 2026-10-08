"""Independent post-Ref final full readback, metadata Ref normal. No namespace/Unit action."""
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
assert subprocess.check_output(['git','diff','HEAD','--','src','tools','pom.xml'],cwd=T)==b''
assert not subprocess.check_output(['git','ls-files','--others','--exclude-standard','--','src','tools'],cwd=T)
proof=json.loads((W/'pg546-readback-v1.safe.json').read_bytes())
assert proof['actualExit']==0 and(W/'pg546-readback-v1.exit').read_text()=='0\n'
assert proof['privateLogSha256']==hashlib.sha256((W/'pg546-readback-v1.private.log').read_bytes()).hexdigest()
RUN='PG547-post-retirement-final-v1';stem=W/RUN.lower();assert not Path(str(stem)+'.private.log').exists()
payload=r'''
import sys,json,os,pathlib,stat,hashlib,dbus
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
tools=pathlib.Path('/var/lib/pgpt-s1-preservation/pg546-post-tools-v1')
assert {p.name for p in tools.iterdir()}==set(HASHES)
for p in tools.iterdir():
 s=p.lstat();assert(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and stat.S_ISREG(s.st_mode)and hashlib.sha256(p.read_bytes()).hexdigest()==HASHES[p.name]
sys.path.insert(0,str(tools))
from pg543_runtime_readback import load
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg546-post-retirement-readback-v1')
old=pathlib.Path('/var/lib/pgpt-s1-preservation/pg543-runtime-retirement-v2')
boundary_raw=(old/'boundaries.private.json').read_bytes();assert hashlib.sha256(boundary_raw).hexdigest()=='0e7fe76e884f918d936842d8bf887c03f816099a11a9a988d022720a13c43726'
env,baseline,snapshot,*_=load(post=True,caddy_before=json.loads(boundary_raw)['caddyExecStartPre'])
strict=env['strict']
assert {p.name for p in root.iterdir()}=={'before.private.json','after.private.json','refs-prepare.private.log','complete.private'}
a=strict(root/'before.private.json',0o600,33554432);b=strict(root/'after.private.json',0o600,33554432)
assert a==b and strict(root/'refs-prepare.private.log',0o600,4096)==b''
complete=strict(root/'complete.private',0o600,4096)
assert complete==b'postRetirementAccepted=true\nallNewScopesReturnedNormally=true\noldCloseUnknownPreserved=true\nruntimeAbsent=true\nstarts0=true\nunlinks0=true\nreloads0=true\ndatabaseUpdates0=true\n'
expected=json.loads(a)
def empty_resources():
 q="select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;"
 assert env['command'](['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-d','schubert_nk','-c',q],4096).splitlines()==[b'0',b'0']
 for name in('maintenance.lock','startup-admission.lock'):
  p=pathlib.Path('/run/schubert-nk')/name;s=p.lstat()
  assert(s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size)==(0,0,stat.S_IFREG|0o600,1,0)
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)>=8 and f[1]=='FLOCK':
    d=f[5].split(':');assert(int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino)
 assert not any(pathlib.Path('/proc',str(p)).exists()for p in(571379,571408,573159,573188))
empty_resources()
bus=dbus.SystemBus(private=True)
manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
refs=[]
for u in env['UNITS']:manager.RefUnit(u);refs.append(u)
assert snapshot()==expected and snapshot()==expected
for u in reversed(refs):manager.UnrefUnit(u)
bus.close();empty_resources()
assert all(env['show'](u,set(v))==v for u,v in expected['units'].items())
for u in env['UNITS']:env['kernel'](u)
assert not os.path.lexists('/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf')
env['command'](['/usr/bin/openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in','/opt/schubert-nk/releases/0.1.0-PG495/RELEASE-MANIFEST.json','-sigfile','/var/lib/pgpt-s1-preservation/pg495-manifest.sig'],4096)
roots={}
for name in('pg546-post-retirement-readback-v1','pg545-runtime-owned-handoff-v1','pg544-runtime-owned-handoff-v1','pg543-runtime-retirement-v2'):
 folder=pathlib.Path('/var/lib/pgpt-s1-preservation')/name
 roots[name]={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in folder.iterdir()}
assert roots['pg546-post-retirement-readback-v1']['before.private.json']==roots['pg546-post-retirement-readback-v1']['after.private.json']
print(json.dumps({'all24Unchanged':True,'batchRows':len(expected['rows']['schubert.batch_runs']),'nativeFiles':sum(v['sha256']is not None for v in expected['native'].values()),'runtimeAbsent':True,'allTenMajor18Unchanged':True,'allBusinessKernelEmpty':True,'peerAdvisoryFlock0':True,'oldFixedPairsAbsent':True,'newMetadataRefsNormallyClosed':True,'signatureCryptographicallyReverified':True,'source':'a2e98ce9e96c42425921e3686e8ae7a94bff9e6c','bomSha256':'f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44','rootProofs':roots,'namespaceUnitActions0':True,'rawExportedToGit':False}))
'''
ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
r=subprocess.run(ssh,input=('HASHES='+repr(proof['toolHashes'])+'\n'+payload).encode(),capture_output=True,timeout=60)
with Path(str(stem)+'.private.log').open('xb')as f:f.write(r.stdout);f.write(r.stderr);f.flush();os.fsync(f.fileno())
with Path(str(stem)+'.exit').open('x')as f:f.write(str(r.returncode)+'\n')
assert r.returncode==0 and not r.stderr
result=json.loads(r.stdout);assert result['batchRows']==462 and result['nativeFiles']==9
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip()==source
safe={'run':RUN,'operatorSource':source,'productionSource':result['source'],'actualExit':r.returncode,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'readback':result,'subjectRun':'PG546-readback-v1','subjectSource':proof['source'],'subjectToolHashes':proof['toolHashes'],'helperSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'privateLogSha256':hashlib.sha256(Path(str(stem)+'.private.log').read_bytes()).hexdigest(),'old143UnknownNotNormalized':True,'formalAccepted':False,'productionPT0':True}
with Path(str(stem)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps({'run':RUN,'actualExit':0,'all24Unchanged':True,'runtimeAbsent':True,'resources0':True,'native9Unchanged':True,'safeSha256':hashlib.sha256(Path(str(stem)+'.safe.json').read_bytes()).hexdigest()}))
