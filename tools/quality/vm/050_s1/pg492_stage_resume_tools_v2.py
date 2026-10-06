"""New-only private fixed operator tool placement, not migration/start or runtime authority."""
import hashlib,json,os,pathlib,shutil,subprocess,tarfile
os.umask(0o077)
R=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
out=W/'pg492-stage-tools-v2';assert not out.exists();out.mkdir(mode=0o700)
for directory in ['pg456-tools-v7','pg481-pending-tools-v2','pg490-migration-tools-v4','pg491-pending-tools-v1','pg492-resume-tools-v2']:
 for file in (W/directory).glob('*.class'):
  target=out/file.name
  if target.exists():assert target.read_bytes()==file.read_bytes()
  else:shutil.copyfile(file,target);target.chmod(0o600)
for name in ['pg492_resume_refs.py','Pg492ResumePreparation.java','Pg492ResumePreparationTest.java']:
 shutil.copyfile(R/'tools/quality/vm/050_s1'/name,out/name);(out/name).chmod(0o600)
files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir()}
assert {'Pg492ResumePreparation.class','Pg492ResumePreparation$References.class','Pg387TrustedDeployment.class','Pg456SignedMigration.class','Pg481PendingDeployment.class','Pg407FailedRootRecovery.class','Pg422SignedMigration.class'}<=set(files)
with (out/'payload-sha256.json').open('x') as f:json.dump(files,f,sort_keys=True)
archive=P/'pg492-resume-tools-v2.tar';assert not archive.exists()
subprocess.run(['tar','-C',str(out),'-cf',str(archive),'.'],check=True)
opts=['-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts')]
ssh=['ssh',*opts,'-p','22222','ubuntu@127.0.0.1'];scp=['scp',*opts,'-P','22222']
subprocess.run(ssh+['test ! -e /home/ubuntu/pg492-tools-stage-v2 && sudo -n test ! -e /var/lib/pgpt-s1-preservation/pg492-resume-tools-v2 && mkdir -m 700 /home/ubuntu/pg492-tools-stage-v2'],check=True)
subprocess.run(scp+[str(archive),'ubuntu@127.0.0.1:/home/ubuntu/pg492-tools-stage-v2/'],check=True)
payload=r'''import pathlib,os,hashlib,json,tarfile,stat
assert os.geteuid()==0
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
archive=pathlib.Path('/home/ubuntu/pg492-tools-stage-v2/pg492-resume-tools-v2.tar')
assert hashlib.sha256(archive.read_bytes()).hexdigest()==DIGEST
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg492-resume-tools-v2');assert not root.exists()
with tarfile.open(archive,'r:') as tar:
 seen=set()
 for member in tar.getmembers():
  p=pathlib.PurePosixPath(member.name);assert not p.is_absolute() and '..' not in p.parts and p.as_posix() not in seen and (member.isdir() or member.isfile());seen.add(p.as_posix())
 root.mkdir(mode=0o700);tar.extractall(root,filter='data')
for file in root.iterdir():
 s=file.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1
 os.chown(file,0,0);os.chmod(file,0o400)
 with file.open('rb') as f:os.fsync(f.fileno())
assert {p.name for p in root.iterdir()}==set(FILES)|{'payload-sha256.json'}
for name,digest in FILES.items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest
assert json.loads((root/'payload-sha256.json').read_text())==FILES
for directory in [root,root.parent]:
 fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print('PG492_OPERATOR_TOOLS_STAGED exactPrivateBytes=true starts0=true ddl0=true currentUnitEpochUnchanged=true')
'''
run=subprocess.run(ssh+['sudo -n python3 -B -'],input=('DIGEST='+repr(hashlib.sha256(archive.read_bytes()).hexdigest())+'\nFILES='+repr(files)+'\n'+payload).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with (W/'pg492-tools-stage-v2-v1.private.log').open('xb') as f:f.write(run.stdout);f.write(run.stderr)
print(run.stdout.decode(),end='')
if run.returncode:print('PG492_OPERATOR_TOOLS_REFUSED actual='+str(run.returncode)+' privateLogs=true partialRetained=true')
raise SystemExit(run.returncode)
