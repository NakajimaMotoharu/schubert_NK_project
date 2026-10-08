"""SSC227 immutable new tool stage/verify/activate, one artifact per mode; no startup."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import time

R=Path(__file__).resolve().parent;T=R.parents[3]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
DEST='/var/lib/pgpt-s1-preservation/pg624-completed-tools-v1'
STAGE='/home/ubuntu/pg624-completed-stage-v1'
PREFIXES=['pg624-completed-tools-v1','pg498-pending-tools-v2','pg481-pending-tools-v1','pg480-backup-tools-v3','pg477-completed-tools-v1','pg477-partial-tools-v3','pg475-readback-tools-v1','pg474-readback-tools-v1','pg473-readback-tools-v1','pg471-readback-tools-v3','pg471-completed-tools-v2','pg469-current-tools-v3','pg468-recovery-tools-v4','pg468-recovery-tools-v2','pg466-tool-v3','pg465-completed-tool-v2','pg464-completed-readback-v7','pg464-code-tools-v2','pg461-known30-tool-v3','pg456-applied-tools-v7']
HOST_PREFIXES=['pg498-pending-tools-v3','pg464-code-tools-v2','pg490-migration-tools-v4','pg481-pending-tools-v2','pg456-tools-v7']


def main():
    os.umask(0o077)
    assert len(sys.argv)==2 and sys.argv[1]in('stage','verify','activate');mode=sys.argv[1]
    assert subprocess.check_output(['git','status','--porcelain'],cwd=T)==b''
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip()
    assert(W/'pg624-compile-v1.private.log').read_bytes()==b''
    oracle=(W/'pg624-oracle-v1.private.log').read_text()
    assert oracle.count('\nOK\n')==5 and 'FAILED'not in oracle and 'PG624_INDEPENDENT_DATA_CLI conditions20=true productionPT0=true' in oracle
    files={n:W/'pg624-completed-tools-v1'/n for n in('Pg624CompletedDeployment.class','Pg624CompletedDeployment$References.class')}
    for n in('pg624_completed_contract.py','pg624_completed_refs.py','pg604_unit_sources.py','pg611_parent_receipt.py'):files[n]=R/n
    hashes={n:hashlib.sha256(p.read_bytes()).hexdigest()for n,p in files.items()}
    dependencies={}
    for name in('Pg464CodeOnlyDeployment.class','Pg387TrustedDeployment.class','Pg387TrustedDeployment$Checked.class','Pg407FailedRootRecovery.class','Pg428ColdBootPreparation.class','Pg481PendingDeployment.class'):
        p=next(W/d/name for d in HOST_PREFIXES if(W/d/name).is_file());dependencies[name]=hashlib.sha256(p.read_bytes()).hexdigest()
    check=r'''
import pathlib,os,stat,hashlib
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
root=pathlib.Path('/var/lib/pgpt-s1-preservation')
for name,sha in DEPENDENCIES.items():
 p=next(root/d/name for d in PREFIXES[1:]if(root/d/name).is_file());s=p.lstat()
 assert stat.S_ISREG(s.st_mode)and s.st_uid==s.st_gid==0 and s.st_nlink==1 and s.st_mode&0o222==0 and hashlib.sha256(p.read_bytes()).hexdigest()==sha
'''
    payload='DEPENDENCIES='+repr(dependencies)+'\nPREFIXES='+repr(PREFIXES)+'\nHASHES='+repr(hashes)+'\nDEST='+repr(DEST)+'\n'+check
    opts=['-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts')]
    ssh=['ssh',*opts,'-p','22222','ubuntu@127.0.0.1']
    log=W/('pg604-'+mode+'-v1.private.log');assert not log.exists()
    assert not(W/('pg604-'+mode+'-v1.safe.json')).exists()
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with log.open('xb')as f:
        if mode=='stage':
            bundle=P/'pg624-completed-tools-v1.tar';assert not bundle.exists()
            with tarfile.open(bundle,'x:')as tar:
                for name,p in sorted(files.items()):tar.add(p,arcname=name,recursive=False)
            subprocess.run(ssh+['test ! -e '+STAGE+' && sudo -n test ! -e '+DEST+' && mkdir -m 700 '+STAGE],check=True,stdout=f,stderr=f)
            subprocess.run(['scp',*opts,'-P','22222',str(bundle),'ubuntu@127.0.0.1:'+STAGE+'/'],check=True,stdout=f,stderr=f)
            payload+='\nBUNDLE='+repr(hashlib.sha256(bundle.read_bytes()).hexdigest())+r'''
import tarfile
p=pathlib.Path('/home/ubuntu/pg624-completed-stage-v1/pg624-completed-tools-v1.tar');assert hashlib.sha256(p.read_bytes()).hexdigest()==BUNDLE
r=pathlib.Path(DEST);assert not os.path.lexists(r);r.mkdir(mode=0o700)
with tarfile.open(p)as tar:
 names=[]
 for member in tar.getmembers():
  assert member.isfile()and member.name in HASHES and member.name not in names;names.append(member.name)
 assert set(names)==set(HASHES);tar.extractall(r,filter='data')
for p in(r,*r.iterdir()):
 s=p.lstat();assert not p.is_symlink()and(stat.S_ISDIR(s.st_mode)or(stat.S_ISREG(s.st_mode)and s.st_nlink==1))
 os.chown(p,0,0);os.chmod(p,0o700 if p.is_dir()else 0o400)
 if p.is_file():assert hashlib.sha256(p.read_bytes()).hexdigest()==HASHES[p.name]
for p in(r,r.parent):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print('PG624_STAGED toolBytesPinned=true businessActions0=true')
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
            cp=':'.join('/var/lib/pgpt-s1-preservation/'+p for p in PREFIXES)+':/opt/schubert-nk/releases/0.1.0-PG600/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG600/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG600/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG600/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
            result=subprocess.run(ssh+['sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" Pg624CompletedDeployment '+mode],stdout=f,stderr=f)
        elapsed=time.monotonic()-began;f.flush();os.fsync(f.fileno())
    with(W/('pg604-'+mode+'-v1.exit')).open('x')as f:f.write(str(result.returncode)+'\n')
    safe={'run':'PG624-'+mode+'-v1','operatorSource':source,'candidateSource':'72fb7440697ee1048a5c0145055dc1cc3c577914','actualExit':result.returncode,'elapsedSeconds':elapsed,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest(),'toolHashes':hashes,'externalDependencyHashes':dependencies,'rawExported':False,'formalAccepted':False,'oldUnknownNormalized':False}
    with(W/('pg604-'+mode+'-v1.safe.json')).open('x')as f:json.dump(safe,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'run':safe['run'],'actualExit':result.returncode,'elapsedSeconds':elapsed,'oldUnknownNormalized':False,'formalAccepted':False}))
    raise SystemExit(result.returncode)


if __name__=='__main__':main()
