"""Immutable stage; distinct once-only failed143 verify/recover. Unknown stays attached."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
GUEST='/var/lib/pgpt-s1-preservation/pg835-pending-tools-v1'
OPTIONS=['-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts')]
SSH=['ssh',*OPTIONS,'-p','22222','ubuntu@127.0.0.1']


def main():
    os.umask(0o077);assert len(sys.argv)==2 and sys.argv[1]in ('stage','activate')
    action=sys.argv[1];assert not subprocess.check_output(['git','status','--porcelain'])
    frozen=json.loads((W/'pg835-frozen-v1.safe.json').read_text());assert type(frozen['actualExit'])is int and frozen['actualExit']==0
    target=W/'pg835-pending-tools-v1';files=frozen['fileHashes']
    assert all(hashlib.sha256((target/name).read_bytes()).hexdigest()==digest for name,digest in files.items())
    base=W/('pg835-'+action+'-v1');assert not any(Path(str(base)+s).exists()for s in ('.private.log','.exit','.safe.json'))
    if action=='stage':
        archive=P/'pg835-pending-tools-v1.tar';assert not archive.exists()
        subprocess.run(['tar','-C',str(target),'-cf',str(archive),'.'],check=True)
        remote='/home/ubuntu/pg835-fixed-stage-v1'
        subprocess.run(SSH+['test ! -e '+remote+' && sudo -n test ! -e '+GUEST+' && mkdir -m700 '+remote],check=True)
        subprocess.run(['scp',*OPTIONS,'-P','22222',str(archive),'ubuntu@127.0.0.1:'+remote+'/'],check=True)
        payload=r'''import pathlib,hashlib,json,os,tarfile,stat
os.umask(0o077);assert os.geteuid()==0
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG796')
archive=pathlib.Path('/home/ubuntu/pg835-fixed-stage-v1/pg835-pending-tools-v1.tar')
assert hashlib.sha256(archive.read_bytes()).hexdigest()==DIGEST
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg835-pending-tools-v1');assert not os.path.lexists(root)
with tarfile.open(archive,'r:')as tar:
 seen=set()
 for m in tar.getmembers():
  p=pathlib.PurePosixPath(m.name);assert not p.is_absolute()and '..'not in p.parts and p.as_posix()not in seen and(m.isdir()and p.as_posix()=='.'or m.isfile()and len(p.parts)==1);seen.add(p.as_posix())
 root.mkdir(mode=0o700);tar.extractall(root,filter='data')
assert {p.name for p in root.iterdir()}==set(FILES)|{'payload-sha256.json'}
for f in root.iterdir():
 s=f.lstat();assert stat.S_ISREG(s.st_mode)and s.st_nlink==1;os.chown(f,0,0);os.chmod(f,0o400)
 with f.open('rb')as stream:os.fsync(stream.fileno())
for name,digest in FILES.items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest
assert json.loads((root/'payload-sha256.json').read_text())==FILES
for d in(root,root.parent):
 fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print('PG835_IMMUTABLE_STAGE filesVerified=true startStopRevoke0=true')
'''
        commands=[(SSH+['sudo -n python3 -B -'],('DIGEST='+repr(hashlib.sha256(archive.read_bytes()).hexdigest())+'\nFILES='+repr(files)+'\n'+payload).encode())]
    else:
        assert (W/'pg835-stage-v1.exit').read_text()=='0\n'
        assert (W/'pg835-candidate-place-v1.exit').read_text()=='0\n'
        cp=GUEST+':/opt/schubert-nk/releases/0.1.0-PG796/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG796/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG796/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG796/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
        prefix='sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" '
        commands=[(SSH+[prefix+'Pg835PendingDeploymentTest'],None),(SSH+[prefix+'Pg835PendingDeployment 2a0d5aa392c85a1dc12a1cdb423978e8500895b8 8bcb3453c182be8f0719818899ec3bd7e86070f7b02086015ecc33c27e10b977'],None)]
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();code=0
    with Path(str(base)+'.private.log').open('xb')as log:
        for args,data in commands:
            result=subprocess.run(args,input=data,stdout=log,stderr=log);log.flush();os.fsync(log.fileno());code=result.returncode
            if code:break
    with Path(str(base)+'.exit').open('x')as f:f.write(str(code)+'\n');f.flush();os.fsync(f.fileno())
    safe={'action':action,'actualExit':code,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'productionSource':frozen['productionSource'],
          'privateLogSha256':hashlib.sha256(Path(str(base)+'.private.log').read_bytes()).hexdigest(),'old143NotNormalized':True,'genuineParentAccepted':False,'formalAccepted':False}
    with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
    print(json.dumps(safe));raise SystemExit(code)


if __name__=='__main__':main()

if __name__=='__main__':
    main()
