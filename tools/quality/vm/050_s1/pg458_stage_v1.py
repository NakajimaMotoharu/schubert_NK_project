"""New-only exact PG458 candidate/tool/observer placement. No activation/DDL/start/permit."""
import hashlib,json,pathlib,re,subprocess,sys
ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
PRIVATE=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
assert len(sys.argv)==2 and re.fullmatch(r'[0-9a-f]{64}',sys.argv[1])
DIGEST=sys.argv[1]
OPTIONS=['-i',str(PRIVATE/'vm-access'),'-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(PRIVATE/'known_hosts')]
SSH=['ssh',*OPTIONS,'-p','22222','ubuntu@127.0.0.1']
SCP=['scp',*OPTIONS,'-P','22222']
FILES={'release.tar':PRIVATE/'pg458-release.tar','manifest.sig':PRIVATE/'pg458-manifest.sig',
       'Pg458CodeOnlyDeployment.class':WORK/'pg458-code-tools-v1/Pg458CodeOnlyDeployment.class',
       'pg458_watch_parent.py':ROOT/'tools/quality/vm/050_s1/pg458_watch_parent.py',
       'pg457_stable_actor.py':ROOT/'tools/quality/vm/050_s1/pg457_stable_actor.py'}
EXPECTED={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in FILES.items()}
subprocess.run(SSH+['umask 077; test ! -e /home/ubuntu/pg458-stage && mkdir /home/ubuntu/pg458-stage'],check=True)
for name,path in FILES.items():subprocess.run(SCP+[str(path),'ubuntu@127.0.0.1:/home/ubuntu/pg458-stage/'+name],check=True)
PAYLOAD='''import hashlib,grp,json,os,pathlib,stat,tarfile
assert os.geteuid()==0 and pathlib.Path('/var/lib/cloud/data/instance-id').read_text().strip()=='pgpt-r2-20260927-01'
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
stage=pathlib.Path('/home/ubuntu/pg458-stage');base=pathlib.Path('/var/lib/pgpt-s1-preservation');release=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG458');tools=base/'pg458-code-tools-v1';sig=base/'pg458-manifest.sig'
for p in (release,tools,sig):assert not p.exists() and not p.is_symlink()
assert set(p.name for p in stage.iterdir())==set(EXPECTED)
for name,digest in EXPECTED.items():
 p=stage/name;s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and hashlib.sha256(p.read_bytes()).hexdigest()==digest
group=grp.getgrnam('schubert').gr_gid
with tarfile.open(stage/'release.tar','r:') as archive:
 members=archive.getmembers();names=set()
 for member in members:
  path=pathlib.PurePosixPath(member.name)
  assert not path.is_absolute() and '..' not in path.parts and (member.isfile() or member.isdir()) and path.as_posix() not in names
  names.add(path.as_posix())
 release.mkdir(mode=0o750);os.chown(release,0,group);archive.extractall(release,filter='data')
manifest=release/'RELEASE-MANIFEST.json';assert hashlib.sha256(manifest.read_bytes()).hexdigest()==DIGEST
data=json.loads(manifest.read_bytes());assert data['release']=='0.1.0-PG458' and data['source']['commit']=='ea1c13aa6a1b0fca2c2f4de1769a7c5afd70244a' and data['versions']['schema']=='027'
for artifact in data['artifacts']:
 p=release/artifact['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==artifact['size'] and hashlib.sha256(p.read_bytes()).hexdigest()==artifact['sha256']
for p in [release,*release.rglob('*')]:
 s=p.lstat();assert not p.is_symlink() and (stat.S_ISDIR(s.st_mode) or (stat.S_ISREG(s.st_mode) and s.st_nlink==1))
 executable=p.relative_to(release).as_posix() in ('operations/bin/schubert-nkctl','operations/bin/schubert-nk-inbox-inspector')
 os.chown(p,0,group);os.chmod(p,0o750 if p.is_dir() or executable else 0o640)
 if p.is_file():
  with p.open('rb') as stream:os.fsync(stream.fileno())
tools.mkdir(mode=0o700)
for name in ('Pg458CodeOnlyDeployment.class','pg458_watch_parent.py','pg457_stable_actor.py'):
 fd=os.open(tools/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o400)
 with os.fdopen(fd,'wb') as stream:stream.write((stage/name).read_bytes());stream.flush();os.fsync(stream.fileno())
 assert hashlib.sha256((tools/name).read_bytes()).hexdigest()==EXPECTED[name]
os.chmod(tools,0o500)
fd=os.open(sig,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o400)
with os.fdopen(fd,'wb') as stream:stream.write((stage/'manifest.sig').read_bytes());stream.flush();os.fsync(stream.fileno())
assert sig.stat().st_size==64 and hashlib.sha256(sig.read_bytes()).hexdigest()==EXPECTED['manifest.sig']
for p in (tools,base,release,release.parent):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print('PG458_STAGE exactSource=true signedCandidateBytes=true rootToolAndStableObserver=true wrapperExecutableMetadata=true previousCurrentUnchanged=true ddl0=true starts0=true permits0=true')
'''
result=subprocess.run(SSH+['sudo -n /usr/bin/python3 -'],input=('EXPECTED='+repr(EXPECTED)+'\nDIGEST='+repr(DIGEST)+'\n'+PAYLOAD).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
print(result.stdout.decode(),end='')
if result.returncode:print('PG458_STAGE_REFUSED actual='+str(result.returncode)+' privateDiagnostics=true')
raise SystemExit(result.returncode)
