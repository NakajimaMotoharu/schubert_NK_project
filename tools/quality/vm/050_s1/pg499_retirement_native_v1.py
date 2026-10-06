"""SSC198 dedicated fixed resume deployment, one operator, private diagnostics only."""
import datetime,hashlib,os,pathlib,subprocess,tarfile
os.umask(0o077)
R=pathlib.Path(__file__).resolve().parent
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
classes=W/'pg499-retirement-tools-v2';dest='/var/lib/pgpt-s1-preservation/pg499-retirement-tools-v1';stage='/home/ubuntu/pg499-retirement-stage-v1'
opts=['-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts')]
ssh=['ssh',*opts,'-p','22222','ubuntu@127.0.0.1'];scp=['scp',*opts,'-P','22222']
assert (W/'pg499-retirement-oracle-v2.private.log').read_text().splitlines()==['PG499_RUNTIME_RETIRE_ORACLE independentAssertions=28 nativeMutation0=true productionPT0=true']
files={p.relative_to(classes).as_posix():p for p in classes.rglob('*.class')};files['pg499_runtime_retirement_refs.py']=R/'pg499_runtime_retirement_refs.py';files['pg499_runtime_retirement_test.py']=R/'pg499_runtime_retirement_test.py';files['pg477_unit_references.py']=R/'pg477_unit_references.py';assert len(files)==5
bundle=P/'pg499-retirement-tools-v1.tar';assert not bundle.exists()
with tarfile.open(bundle,'x:') as tar:
 for name,p in sorted(files.items()):tar.add(p,arcname=name,recursive=False)
hashes={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in files.items()}
subprocess.run(ssh+['test ! -e '+stage+' && sudo -n test ! -e '+dest+' && sudo -n test ! -e /var/lib/pgpt-s1-preservation/pg499-runtime-retirement && mkdir -m 700 '+stage],check=True)
subprocess.run(scp+[str(bundle),'ubuntu@127.0.0.1:'+stage+'/'],check=True,stdout=subprocess.DEVNULL)
payload=r'''import pathlib,os,tarfile,hashlib,stat
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
p=pathlib.Path('/home/ubuntu/pg499-retirement-stage-v1/pg499-retirement-tools-v1.tar');assert hashlib.sha256(p.read_bytes()).hexdigest()==BUNDLE
r=pathlib.Path('/var/lib/pgpt-s1-preservation/pg499-retirement-tools-v1');assert not r.exists();r.mkdir(mode=0o700)
with tarfile.open(p) as t:
 names=[]
 for m in t.getmembers():
  v=pathlib.PurePosixPath(m.name);assert m.isfile() and not v.is_absolute() and '..' not in v.parts and m.name in HASHES;names.append(m.name)
 assert len(names)==len(set(names))==len(HASHES);t.extractall(r,filter='data')
for p in [r,*r.rglob('*')]:
 s=p.lstat();assert not p.is_symlink() and (stat.S_ISDIR(s.st_mode) or stat.S_ISREG(s.st_mode) and s.st_nlink==1);os.chown(p,0,0);os.chmod(p,0o700 if p.is_dir() else 0o400)
 if p.is_file():assert hashlib.sha256(p.read_bytes()).hexdigest()==HASHES[p.relative_to(r).as_posix()]
for d in [p for p in r.rglob('*') if p.is_dir()]+[r,r.parent]:
 fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print('PG481_STAGED fixedClassBytes=true immutable400=true starts0=true')
'''
log=W/'pg499-retirement-native-v1.private.log';assert not log.exists()
with log.open('xb') as f:
 f.write((datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n').encode());f.flush()
 staged=subprocess.run(ssh+['sudo -n python3 -B -'],input=('HASHES='+repr(hashes)+'\nBUNDLE='+repr(hashlib.sha256(bundle.read_bytes()).hexdigest())+'\n'+payload).encode(),stdout=f,stderr=f);assert staged.returncode==0
 prefixes=['pg499-retirement-tools-v1','pg498-pending-tools-v2','pg481-pending-tools-v1','pg480-backup-tools-v3','pg477-completed-tools-v1','pg477-partial-tools-v3','pg475-readback-tools-v1','pg474-readback-tools-v1','pg473-readback-tools-v1','pg471-readback-tools-v3','pg471-completed-tools-v2','pg469-current-tools-v3','pg468-recovery-tools-v4','pg468-recovery-tools-v2','pg466-tool-v3','pg465-completed-tool-v2','pg464-completed-readback-v7','pg464-code-tools-v2','pg461-known30-tool-v3','pg456-applied-tools-v7']
 cp=':'.join('/var/lib/pgpt-s1-preservation/'+p for p in prefixes)+':/opt/schubert-nk/releases/0.1.0-PG495/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG495/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG495/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG495/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
 test=subprocess.run(ssh+['sudo -n python3 -B '+dest+'/pg499_runtime_retirement_test.py'],stdout=f,stderr=f);assert test.returncode==0
 result=subprocess.run(ssh+['sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" Pg499RuntimeRetirement retire'],stdout=f,stderr=f)
 f.write((datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n').encode());f.flush();os.fsync(f.fileno())
with (W/'pg499-retirement-native-v1.exit').open('x') as f:f.write(str(result.returncode)+'\n')
print('PG481_PREPARED_RESUME_NATIVE actual='+str(result.returncode)+' oldCloseNotInferred=true logsPrivate=true');raise SystemExit(result.returncode)
