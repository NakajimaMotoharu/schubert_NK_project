"""Once-only immutable recursive ABI stage and one-role preparation; no other actions."""
import datetime
import hashlib
import json
import os
from pathlib import Path,PurePosixPath
import subprocess
import sys

W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
SOURCE='769ddb15cd735c25fef581b5f9850ef9d0053c0f'
GUEST='/var/lib/pgpt-s1-preservation/pg1374-bootstrap-role-tools-v2'
OPTIONS=['-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts')]
SSH=['ssh',*OPTIONS,'-p','22222','ubuntu@127.0.0.1']

STAGE=r'''import pathlib,hashlib,json,os,stat,tarfile
os.umask(0o077)
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cbca8738-3b24-4090-b77c-bf029677cdd6'
assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1292')
archive=pathlib.Path('/home/ubuntu/pg1374-bootstrap-role-stage-v2/pg1374-bootstrap-role-tools-v2.tar');assert hashlib.sha256(archive.read_bytes()).hexdigest()==DIGEST
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1374-bootstrap-role-tools-v2');assert not os.path.lexists(root)
directories={'.'}
for name in FILES:
 p=pathlib.PurePosixPath(name);assert not p.is_absolute()and '..'not in p.parts
 for ancestor in p.parents:
  directories.add(str(ancestor))
with tarfile.open(archive,'r:')as tar:
 seen=set()
 for m in tar.getmembers():
  p=pathlib.PurePosixPath(m.name);n=str(p);assert not p.is_absolute()and '..'not in p.parts and n not in seen
  assert m.isdir()and n in directories or m.isfile()and n in set(FILES)|{'payload-sha256.json'}
  seen.add(n)
 assert seen==directories|set(FILES)|{'payload-sha256.json'}
 root.mkdir(mode=0o700);tar.extractall(root,filter='data')
actual={str(p.relative_to(root))for p in root.rglob('*')if p.is_file()};assert actual==set(FILES)|{'payload-sha256.json'}
for p in root.rglob('*'):
 s=p.lstat();assert not p.is_symlink()
 if p.is_dir():os.chown(p,0,0);os.chmod(p,0o700)
 else:
  assert stat.S_ISREG(s.st_mode)and s.st_nlink==1;os.chown(p,0,0);os.chmod(p,0o400)
  with p.open('rb')as f:os.fsync(f.fileno())
for name,digest in FILES.items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest
assert json.loads((root/'payload-sha256.json').read_bytes())==FILES
for p in [*sorted((p for p in root.rglob('*')if p.is_dir()),key=lambda p:len(p.parts),reverse=True),root,root.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print('PG1377_ROLE_IMMUTABLE_STAGE filesVerified=true businessActions0=true')
'''

def qualify(frozen,preflight):
    if type(frozen)is not dict or type(frozen.get('actualExit'))is not int or frozen['actualExit']!=0 or frozen.get('productionSource')!=SOURCE or type(frozen.get('roleByteOracleExit'))is not int or frozen['roleByteOracleExit']!=0:raise ValueError('qualified exact current full management ABI required')
    if type(preflight)is not dict or type(preflight.get('actualExit'))is not int or preflight['actualExit']!=0 or preflight.get('productionSource')!=SOURCE or preflight.get('run')!='PG1376-bootstrap-role-preflight-v1' or preflight.get('allClientAdvisoryFlock0')is not True:raise ValueError('fresh actual fullcurrent missingrole guard required')
    files=frozen.get('fileHashes')
    if type(files)is not dict or not files or 'Pg1374BootstrapRolePreparation.class'not in files or 'pg1374_bootstrap_role_refs.py'not in files:raise ValueError('complete producer-consumer file graph required')
    for name,digest in files.items():
        if type(name)is not str:raise ValueError('string relative ABI path required')
        path=PurePosixPath(name)
        if type(name)is not str or path.is_absolute()or '..'in path.parts or str(path)!=name or type(digest)is not str or len(digest)!=64 or any(c not in '0123456789abcdef'for c in digest):raise ValueError('exact relative ABI hash required')
    return files

def main():
    os.umask(0o077)
    if sys.argv[1:]not in(['stage'],['prepare']):raise ValueError('fixed role phase required')
    action=sys.argv[1]
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed tool source required')
    if(W/'pg1368-bootstrap-fixed-ref-handoff-v1.exit').read_bytes()!=b'0\n':raise ValueError('old exact owner already recovered required')
    build=json.loads((W/'pg1375-frozen-v2.safe.json').read_bytes());guard=json.loads((W/'pg1376-bootstrap-role-preflight-v1.safe.json').read_bytes());files=qualify(build,guard)
    target=W/'pg1374-bootstrap-role-tools-v2'
    if any(hashlib.sha256((target/n).read_bytes()).hexdigest()!=d for n,d in files.items()):raise ValueError('exact qualified output ABI bytes required')
    if action=='prepare'and(W/'pg1377-stage-v1.exit').read_bytes()!=b'0\n':raise ValueError('normal complete immutable stage required')
    base=W/('pg1377-'+action+'-v1')
    if any(Path(str(base)+suffix).exists()for suffix in('.requested','.exit','.safe.json','.private.log')):raise ValueError('new-only phase required')
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();start=datetime.datetime.now(datetime.timezone.utc)
    with Path(str(base)+'.requested').open('x')as f:f.write('oneDispatch=true\n');f.flush();os.fsync(f.fileno())
    fd=os.open(W,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
    if action=='stage':
        archive=P/'pg1374-bootstrap-role-tools-v2.tar'
        if archive.exists():raise ValueError('new-only archive required')
        subprocess.run(['tar','-C',str(target),'-cf',str(archive),'.'],check=True)
        remote='/home/ubuntu/pg1374-bootstrap-role-stage-v2'
        subprocess.run(SSH+['test ! -e '+remote+' && sudo -n test ! -e '+GUEST+' && mkdir -m700 '+remote],check=True)
        subprocess.run(['scp',*OPTIONS,'-P','22222',str(archive),'ubuntu@127.0.0.1:'+remote+'/'],check=True)
        code='DIGEST='+repr(hashlib.sha256(archive.read_bytes()).hexdigest())+'\nFILES='+repr(files)+'\n'+STAGE;compile(code,'<actual recursive stage>','exec')
        commands=[(SSH+['sudo -n python3 -B -'],code.encode())]
    else:
        cp=GUEST+':/opt/schubert-nk/releases/0.1.0-PG1292/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG1292/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG1292/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG1292/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
        command='sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" '
        commands=[(SSH+[command+'Pg1374BootstrapRoleArgumentTest'],None),(SSH+[command+'Pg1374BootstrapRolePreparation prepare'],None)]
    code=0
    with Path(str(base)+'.private.log').open('xb')as log:
        for argv,data in commands:
            result=subprocess.run(argv,input=data,stdout=log,stderr=log);log.flush();os.fsync(log.fileno());code=result.returncode
            if code:break
    result={'action':action,'actualExit':code,'operatorSourceAtStart':head,'operatorHeadAtEnd':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'productionSource':SOURCE,'startedUTC':start.isoformat(),'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'privateLogSha256':hashlib.sha256(Path(str(base)+'.private.log').read_bytes()).hexdigest(),'formalAccepted':False}
    with Path(str(base)+'.exit').open('x')as f:f.write(str(code)+'\n');f.flush();os.fsync(f.fileno())
    with Path(str(base)+'.safe.json').open('x')as f:json.dump(result,f,sort_keys=True)
    print(json.dumps(result));return code

if __name__=='__main__':raise SystemExit(main())
