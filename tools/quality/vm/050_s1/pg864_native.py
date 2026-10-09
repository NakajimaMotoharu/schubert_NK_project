"""One dispatch per fixed new v2 stage/RO preparation/verify/finite activation."""
import datetime,hashlib,json,os,subprocess,sys,tarfile
from pathlib import Path
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private');G='/var/lib/pgpt-s1-preservation/pg864-completed-tools-v2'
OPTS=['-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts')]
SSH=['ssh',*OPTS,'-p','22222','ubuntu@127.0.0.1']
if __name__=='__main__':
 os.umask(0o077);assert len(sys.argv)==2 and sys.argv[1]in ('stage','prepare-ro','verify','activate');action=sys.argv[1]
 assert subprocess.check_output(['git','status','--porcelain'])==b''
 frozen=json.loads((W/'pg864-frozen-v2.safe.json').read_bytes());assert frozen['run']=='PG864-compile-v2'and frozen['actualExit']==0
 target=W/'pg864-completed-tools-v2';files=frozen['fileHashes']
 assert all(hashlib.sha256((target/name).read_bytes()).hexdigest()==digest for name,digest in files.items())
 base=W/('pg864-'+action+'-v2');assert not any(Path(str(base)+s).exists()for s in ('.private.log','.safe.json','.exit'))
 if action=='stage':
  archive=P/'pg864-completed-tools-v2.tar'
  with tarfile.open(archive,'x:')as tar:
   for f in sorted(target.iterdir()):assert f.is_file()and not f.is_symlink();tar.add(f,arcname=f.name,recursive=False)
  remote='/home/ubuntu/pg864-stage-v2'
  subprocess.run(SSH+['test ! -e '+remote+' && sudo -n test ! -e '+G+' && mkdir -m700 '+remote],check=True)
  subprocess.run(['scp',*OPTS,'-P','22222',str(archive),'ubuntu@127.0.0.1:'+remote+'/'],check=True)
  payload='''import pathlib,hashlib,json,os,stat,tarfile
os.umask(0o077);assert os.geteuid()==0
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG832')
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg864-completed-tools-v2');assert not os.path.lexists(root)
archive=pathlib.Path('/home/ubuntu/pg864-stage-v2/pg864-completed-tools-v2.tar');assert hashlib.sha256(archive.read_bytes()).hexdigest()==DIGEST
with tarfile.open(archive,'r:')as tar:
 seen=set()
 for m in tar.getmembers():
  p=pathlib.PurePosixPath(m.name);assert len(p.parts)==1 and not p.is_absolute()and p.name not in seen and m.isfile();seen.add(p.name)
 assert seen==set(FILES)|{'payload-sha256.json'}
 root.mkdir(mode=0o700);tar.extractall(root,filter='data')
for f in root.iterdir():
 s=f.lstat();assert stat.S_ISREG(s.st_mode)and s.st_nlink==1;os.chown(f,0,0);os.chmod(f,0o400)
 with f.open('rb')as q:os.fsync(q.fileno())
assert {p.name for p in root.iterdir()}==set(FILES)|{'payload-sha256.json'}
for name,digest in FILES.items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest
assert json.loads((root/'payload-sha256.json').read_bytes())==FILES
for p in (root,root.parent):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print('PG864_IMMUTABLE_STAGE files98=true startStopPublish0=true')
'''
  commands=[(SSH+['sudo -n python3 -B -'],('DIGEST='+repr(hashlib.sha256(archive.read_bytes()).hexdigest())+'\nFILES='+repr(files)+'\n'+payload).encode())]
 else:
  stage=json.loads((W/'pg864-stage-v2.safe.json').read_bytes());assert stage['actualExit']==0 and stage['run']=='PG864-stage-v2'
  if action=='verify':assert json.loads((W/'pg864-prepare-ro-v2.safe.json').read_bytes())['actualExit']==0
  if action=='activate':assert json.loads((W/'pg864-verify-v2.safe.json').read_bytes())['actualExit']==0
  cp=G+':/opt/schubert-nk/releases/0.1.0-PG832/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG832/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG832/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG832/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
  prefix='sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" '
  commands=[(SSH+[prefix+'Pg864CompletedDeploymentTest'],None),(SSH+[prefix+'Pg864CompletedDeployment '+action],None)]
 start=datetime.datetime.now(datetime.timezone.utc);code=0
 with Path(str(base)+'.private.log').open('xb')as f:
  for args,data in commands:
   r=subprocess.run(args,input=data,stdout=f,stderr=f);f.flush();os.fsync(f.fileno());code=r.returncode
   if code:break
 safe={'run':'PG864-'+action+'-v2','action':action,'actualExit':code,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'compileOperator':frozen['operatorSource'],'installedSource':frozen['installedSource'],'candidateSource':frozen['candidateSource'],'startedUTC':start.isoformat(),'elapsedSeconds':(datetime.datetime.now(datetime.timezone.utc)-start).total_seconds(),'privateLogSha256':hashlib.sha256(Path(str(base)+'.private.log').read_bytes()).hexdigest(),'old143NotNormalized':True,'genuineParentAccepted':False,'formalAccepted':False}
 with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,indent=2);f.flush();os.fsync(f.fileno())
 with Path(str(base)+'.exit').open('x')as f:f.write(str(code)+'\n');f.flush();os.fsync(f.fileno())
 print(json.dumps(safe));raise SystemExit(code)
