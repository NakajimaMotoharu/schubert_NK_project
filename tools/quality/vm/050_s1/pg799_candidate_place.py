"""New-only signed796 payload placement; never changes current/approval/epoch/Unit."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
from pg799_pending_sources import SOURCE,DIGEST,OLD_SOURCE,OLD_DIGEST

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')

PAYLOAD=r'''
import pathlib,os,hashlib,tarfile,grp,stat
os.umask(0o077);assert os.geteuid()==0
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
assert pathlib.Path('/var/lib/cloud/data/instance-id').read_text().strip()=='pgpt-r2-20260927-01'
assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG750')
assert hashlib.sha256(pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()).hexdigest()==OLD_DIGEST
stage=pathlib.Path('/home/ubuntu/pg796-release-stage-v1');archive=stage/'pg796-release-v1.tar';signature=stage/'pg796-manifest-v1.sig'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==ARCHIVE and hashlib.sha256(signature.read_bytes()).hexdigest()==SIGNATURE
candidate=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG796');private=pathlib.Path('/var/lib/pgpt-s1-preservation/pg796-manifest.sig')
assert not os.path.lexists(candidate)and not os.path.lexists(private)
with tarfile.open(archive)as tar:
 seen=set()
 for member in tar.getmembers():
  name=pathlib.PurePosixPath(member.name)
  assert not name.is_absolute()and '..'not in name.parts and name.as_posix()not in seen and(member.isfile()or member.isdir());seen.add(name.as_posix())
 candidate.mkdir(mode=0o750);tar.extractall(candidate,filter='data')
group=grp.getgrnam('schubert').gr_gid
for path in(candidate,*candidate.rglob('*')):
 s=path.lstat();assert not path.is_symlink()and(stat.S_ISDIR(s.st_mode)or stat.S_ISREG(s.st_mode)and s.st_nlink==1)
 os.chown(path,0,group);os.chmod(path,0o750 if path.is_dir()or path.name=='schubert-nk-inbox-inspector'else 0o640)
 if path.is_file():
  with path.open('rb')as f:os.fsync(f.fileno())
assert {p.relative_to(candidate).as_posix()for p in candidate.rglob('*')if p.is_file()}==set(FILES)
for name,digest in FILES.items():assert hashlib.sha256((candidate/name).read_bytes()).hexdigest()==digest
assert hashlib.sha256((candidate/'RELEASE-MANIFEST.json').read_bytes()).hexdigest()==DIGEST
with private.open('xb')as f:os.fchmod(f.fileno(),0o400);f.write(signature.read_bytes());f.flush();os.fsync(f.fileno())
for path in(candidate,candidate.parent,private.parent):
 fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print('PG796_CANDIDATE_PLACED signedPayloadPinned=true currentApprovalEpochUnitUnchanged=true runtimeActions0=true')
'''

def main():
 os.umask(0o077);assert not subprocess.check_output(['git','status','--porcelain'])
 head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();candidate=W/'pg796-release-v1';sig=P/'pg796-manifest-v1.sig'
 safe=json.loads((W/'pg796-candidate-build-v1.safe.json').read_text());assert safe['candidateSource']==SOURCE and safe['priorSource']==OLD_SOURCE and safe['manifestSha256']==DIGEST and safe['signatureVerified']and safe['artifacts']==187
 assert not subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml'])
 assert hashlib.sha256(sig.read_bytes()).hexdigest()==safe['signatureSha256']and len(sig.read_bytes())==64
 files={p.relative_to(candidate).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in candidate.rglob('*')if p.is_file()}
 assert hashlib.sha256((candidate/'RELEASE-MANIFEST.json').read_bytes()).hexdigest()==DIGEST
 archive=P/'pg796-release-v1.tar';assert not archive.exists()
 with tarfile.open(archive,'x:')as tar:
  for path in sorted(candidate.rglob('*')):assert not path.is_symlink();tar.add(path,arcname=path.relative_to(candidate).as_posix(),recursive=False)
 base=W/'pg799-candidate-place-v1';assert not any(Path(str(base)+s).exists()for s in ('.private.log','.exit','.safe.json'))
 opts=['-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts')];ssh=['ssh',*opts,'-p','22222','ubuntu@127.0.0.1']
 started=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with Path(str(base)+'.private.log').open('xb')as log:
  subprocess.run(ssh+['test ! -e /home/ubuntu/pg796-release-stage-v1 && sudo -n test ! -e /opt/schubert-nk/releases/0.1.0-PG796 && mkdir -m700 /home/ubuntu/pg796-release-stage-v1'],stdout=log,stderr=log,check=True)
  subprocess.run(['scp',*opts,'-P','22222',str(archive),str(sig),'ubuntu@127.0.0.1:/home/ubuntu/pg796-release-stage-v1/'],stdout=log,stderr=log,check=True)
  payload='ARCHIVE='+repr(hashlib.sha256(archive.read_bytes()).hexdigest())+'\nSIGNATURE='+repr(safe['signatureSha256'])+'\nFILES='+repr(files)+'\nDIGEST='+repr(DIGEST)+'\nOLD_DIGEST='+repr(OLD_DIGEST)+'\n'+PAYLOAD
  result=subprocess.run(ssh+['sudo -n python3 -B -'],input=payload.encode(),stdout=log,stderr=log);log.flush();os.fsync(log.fileno())
 with Path(str(base)+'.exit').open('x')as f:f.write(str(result.returncode)+'\n')
 safe={'actualExit':result.returncode,'operatorSource':head,'candidateSource':SOURCE,'manifestSha256':DIGEST,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'privateLogSha256':hashlib.sha256(Path(str(base)+'.private.log').read_bytes()).hexdigest(),'currentApprovalEpochUnitUnchangedRequired':True,'formalAccepted':False}
 with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
 print(json.dumps(safe));raise SystemExit(result.returncode)

if __name__=='__main__':main()
