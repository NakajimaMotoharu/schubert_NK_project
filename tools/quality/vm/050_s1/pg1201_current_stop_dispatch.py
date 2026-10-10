"""New immutable D5 tools then current-only reverse stop, no start authority."""
import datetime
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
from pg1199_current_stop_compile import proof
from pg1198_current_stop_binding import generate, bindings, SOURCE, BEFORE

W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
GUEST='/var/lib/pgpt-s1-preservation/pg1198-native-tools-v1'
OPTIONS=['-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts')]
SSH=['ssh',*OPTIONS,'-p','22222','ubuntu@127.0.0.1']


def archive_members(members, files):
    from pathlib import PurePosixPath
    if type(members)is not list or type(files)is not set or not files:
        raise ValueError('archive schema refused')
    dirs={str(parent)for name in files for parent in PurePosixPath(name).parents if str(parent)!='.'}
    seen=set();found_files=set();found_dirs=set()
    for name,kind in members:
        p=PurePosixPath(name)
        if type(name)is not str or not name or p.is_absolute()or '..'in p.parts or p.as_posix()!=name or name in seen or kind not in {'file','dir'}:
            raise ValueError('archive member refused')
        seen.add(name)
        (found_files if kind=='file'else found_dirs).add(name)
    if found_files!=files or found_dirs!=dirs:raise ValueError('archive exact closure refused')


STAGE=r'''
import pathlib,hashlib,json,os,tarfile,stat
os.umask(0o077);assert os.geteuid()==0
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cbca8738-3b24-4090-b77c-bf029677cdd6'
assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1068')
archive=pathlib.Path('/home/ubuntu/pg1201-fixed-stage-v1/pg1198-native-tools-v1.tar')
assert hashlib.sha256(archive.read_bytes()).hexdigest()==DIGEST
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1198-native-tools-v1');assert not os.path.lexists(root)
with tarfile.open(archive,'r:')as tar:
 members=tar.getmembers();archive_members([(m.name,'file'if m.isfile()else'dir'if m.isdir()else'unsupported')for m in members],set(FILES)|{'payload-sha256.json'})
 root.mkdir(mode=0o700);tar.extractall(root,filter='data')
for p in root.rglob('*'):
 s=p.lstat();assert not p.is_symlink();os.chown(p,0,0)
 if p.is_dir():os.chmod(p,0o700)
 else:
  assert stat.S_ISREG(s.st_mode)and s.st_nlink==1;os.chmod(p,0o400)
  with p.open('rb')as f:os.fsync(f.fileno())
for name,digest in FILES.items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest
assert json.loads((root/'payload-sha256.json').read_bytes())==FILES
for d in sorted([root,*[p for p in root.rglob('*')if p.is_dir()]],key=lambda p:len(p.parts),reverse=True)+[root.parent]:
 fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print('PG1201_IMMUTABLE_STAGE filesVerified=true startsStops0=true')
'''
STAGE=inspect.getsource(archive_members)+'\n'+STAGE


def main():
    os.umask(0o077)
    if sys.argv[1:]not in (['stage'],['stop']):raise ValueError('stage or stop required')
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean frozen source required')
    action=sys.argv[1];p=proof();bindings(p)
    frozen=json.loads((W/'pg1199-frozen-v1.safe.json').read_bytes())
    if frozen['actualExit']!=0 or frozen['productionSource']!=SOURCE or frozen['genuineParentBeforeSha256']!=BEFORE:raise ValueError('qualified current frozen payload required')
    pre=json.loads((W/'pg1200-current-stop-preflight-v1.safe.json').read_bytes())
    if pre['actualExit']!=0 or not pre['fullCurrentBeforeIdentical']:raise ValueError('actual full current preflight required')
    target=W/'pg1198-native-tools-v1';files=frozen['fileHashes']
    for name,digest in files.items():
        if hashlib.sha256((target/name).read_bytes()).hexdigest()!=digest:raise ValueError('immutable SHA refused')
    for name,raw in generate(p).items():
        if (target/name).read_text()!=raw:raise ValueError('generated source changed')
    base=W/('pg1201-'+action+'-v1')
    if any(Path(str(base)+s).exists()for s in('.private.log','.exit','.safe.json')):raise ValueError('new-only dispatch slot required')
    if action=='stage':
        archive=P/'pg1198-native-tools-v1.tar'
        with tarfile.open(archive,'x:')as tar:
            for f in sorted(target.rglob('*')):tar.add(f,arcname=str(f.relative_to(target)),recursive=False)
        remote='/home/ubuntu/pg1201-fixed-stage-v1'
        subprocess.run(SSH+['test ! -e '+remote+' && sudo -n test ! -e '+GUEST+' && mkdir -m700 '+remote],check=True)
        subprocess.run(['scp',*OPTIONS,'-P','22222',str(archive),'ubuntu@127.0.0.1:'+remote+'/'],check=True)
        commands=[(SSH+['sudo -n python3 -B -'],('DIGEST='+repr(hashlib.sha256(archive.read_bytes()).hexdigest())+'\nFILES='+repr(files)+'\n'+STAGE).encode())]
    else:
        if (W/'pg1201-stage-v1.exit').read_bytes()!=b'0\n':raise ValueError('actual immutable stage required')
        cp=GUEST+':/opt/schubert-nk/releases/0.1.0-PG1068/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG1068/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG1068/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG1068/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
        prefix='sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" '
        commands=[(SSH+[prefix+'Pg1198NativeArgumentTest'],None),(SSH+[prefix+'Pg1198NativeStop stop'],None)]
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();code=0
    with Path(str(base)+'.private.log').open('xb')as log:
        for args,data in commands:
            result=subprocess.run(args,input=data,stdout=log,stderr=log);log.flush();os.fsync(log.fileno());code=result.returncode
            if code:break
    with Path(str(base)+'.exit').open('x')as f:f.write(str(code)+'\n');f.flush();os.fsync(f.fileno())
    safe={'action':action,'actualExit':code,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'productionSource':SOURCE,'privateLogSha256':hashlib.sha256(Path(str(base)+'.private.log').read_bytes()).hexdigest(),'oldFailedNormalized':False,'starts0':True,'formalAccepted':False}
    with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
    print(json.dumps(safe));return code


if __name__=='__main__':raise SystemExit(main())
