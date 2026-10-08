"""SSC190 completed-only verify/activate, pinned source, new-only roots; no startup."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import time

os.umask(0o077)
R=Path(__file__).resolve().parent; T=R.parents[3]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379'); P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
DEST='/var/lib/pgpt-s1-preservation/pg549-completed-tools-v3'
STAGE='/home/ubuntu/pg549-completed-stage-v3'
opts=['-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts')]
ssh=['ssh',*opts,'-p','22222','ubuntu@127.0.0.1']
assert len(sys.argv)==2 and sys.argv[1] in ('stage','verify','activate')
mode=sys.argv[1]
assert subprocess.check_output(['git','status','--porcelain'],cwd=T)==b''
source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip()
assert (W/'pg549-completed-compile-v3.private.log').read_bytes()==b''
classes=W/'pg549-completed-tools-v3'
files={p.name:p for p in classes.glob('*.class')if p.name!='Pg549CompletedDeploymentTest.class'}
for name in ('pg543_retirement_contract.py','pg543_runtime_readback.py','pg549_completed_refs.py','pg542_current_contract.py'):files[name]=R/name
files['pg549_completed_contract.py']=R/'pg549_completed_contract.py'
assert len(files)==7
hashes={n:hashlib.sha256(p.read_bytes()).hexdigest()for n,p in files.items()}
prefixes=['pg549-completed-tools-v3','pg498-pending-tools-v3','pg481-pending-tools-v1','pg480-backup-tools-v3','pg477-completed-tools-v1','pg477-partial-tools-v3','pg475-readback-tools-v1','pg474-readback-tools-v1','pg473-readback-tools-v1','pg471-readback-tools-v3','pg471-completed-tools-v3','pg469-current-tools-v3','pg468-recovery-tools-v4','pg468-recovery-tools-v3','pg466-tool-v3','pg465-completed-tool-v3','pg464-completed-readback-v7','pg464-code-tools-v3','pg461-known30-tool-v3','pg456-applied-tools-v7']
host_prefixes=['pg498-pending-tools-v3','pg464-code-tools-v3','pg490-migration-tools-v4','pg481-pending-tools-v3','pg456-tools-v7']
dependencies={}
for name in ('Pg464CodeOnlyDeployment.class','Pg387TrustedDeployment.class','Pg387TrustedDeployment$Checked.class','Pg407FailedRootRecovery.class','Pg428ColdBootPreparation.class','Pg481PendingDeployment.class'):
    p=next(W/d/name for d in host_prefixes if(W/d/name).is_file());dependencies[name]=hashlib.sha256(p.read_bytes()).hexdigest()
check=r'''
import pathlib,os,stat,hashlib
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
root=pathlib.Path('/var/lib/pgpt-s1-preservation')
for name,sha in DEPENDENCIES.items():
 p=next(root/d/name for d in PREFIXES[1:] if(root/d/name).is_file());s=p.lstat()
 assert stat.S_ISREG(s.st_mode)and s.st_uid==s.st_gid==0 and s.st_nlink==1 and s.st_mode&0o222==0 and hashlib.sha256(p.read_bytes()).hexdigest()==sha
'''
payload='DEPENDENCIES='+repr(dependencies)+'\nPREFIXES='+repr(prefixes)+'\nHASHES='+repr(hashes)+'\nDEST='+repr(DEST)+'\n'+check
started=datetime.datetime.now(datetime.timezone.utc).isoformat(); log=W/('pg549-'+mode+'-v3.private.log');assert not log.exists()
with log.open('xb')as f:
    if mode=='stage':
        bundle=P/'pg549-completed-tools-v3.tar';assert not bundle.exists()
        with tarfile.open(bundle,'x:')as tar:
            for name,p in sorted(files.items()):tar.add(p,arcname=name,recursive=False)
        subprocess.run(ssh+['test ! -e '+STAGE+' && sudo -n test ! -e '+DEST+' && mkdir -m 700 '+STAGE],check=True,stdout=f,stderr=f)
        subprocess.run(['scp',*opts,'-P','22222',str(bundle),'ubuntu@127.0.0.1:'+STAGE+'/'],check=True,stdout=f,stderr=f)
        payload+='\nBUNDLE='+repr(hashlib.sha256(bundle.read_bytes()).hexdigest())+r'''
import tarfile
p=pathlib.Path('/home/ubuntu/pg549-completed-stage-v3/pg549-completed-tools-v3.tar');assert hashlib.sha256(p.read_bytes()).hexdigest()==BUNDLE
r=pathlib.Path(DEST);assert not r.exists();r.mkdir(mode=0o700)
with tarfile.open(p)as t:
 names=[]
 for m in t.getmembers():
  v=pathlib.PurePosixPath(m.name);assert m.isfile()and not v.is_absolute()and '..'not in v.parts and m.name in HASHES;names.append(m.name)
 assert len(names)==len(set(names))==len(HASHES);t.extractall(r,filter='data')
for p in [r,*r.iterdir()]:
 s=p.lstat();assert not p.is_symlink()and(stat.S_ISDIR(s.st_mode)or stat.S_ISREG(s.st_mode)and s.st_nlink==1);os.chown(p,0,0);os.chmod(p,0o700 if p.is_dir()else 0o400)
 if p.is_file():assert hashlib.sha256(p.read_bytes()).hexdigest()==HASHES[p.name]
for p in (r,r.parent):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print('PG549_STAGED toolBytesPinned=true businessActions0=true')
'''
    else:
        payload+=r'''
r=pathlib.Path(DEST);assert {p.name for p in r.iterdir()}==set(HASHES)
for p in r.iterdir():
 s=p.lstat();assert stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and hashlib.sha256(p.read_bytes()).hexdigest()==HASHES[p.name]
'''
    began=time.monotonic()
    result=subprocess.run(ssh+['sudo -n python3 -B -'],input=payload.encode(),stdout=f,stderr=f,timeout=90)
    if result.returncode==0 and mode!='stage':
        cp=':'.join('/var/lib/pgpt-s1-preservation/'+p for p in prefixes)+':/opt/schubert-nk/releases/0.1.0-PG495/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG495/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG495/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG495/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
        result=subprocess.run(ssh+['sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" Pg549CompletedDeployment '+mode],stdout=f,stderr=f)
    elapsed=time.monotonic()-began;f.flush();os.fsync(f.fileno())
with(W/('pg549-'+mode+'-v3.exit')).open('x')as f:f.write(str(result.returncode)+'\n')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip()==source
safe={'source':source,'run':'PG549-'+mode+'-v3','mode':mode,'actualExit':result.returncode,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsedSeconds':elapsed,'toolHashes':hashes,'dependencyHashes':dependencies,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest(),'formalAccepted':False,'productionPT0':True,'oldCloseNotInferred':True}
with(W/('pg549-'+mode+'-v3.safe.json')).open('x')as f:json.dump(safe,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps({'run':safe['run'],'actualExit':result.returncode,'elapsedSeconds':elapsed,'formalAccepted':False}));raise SystemExit(result.returncode)
