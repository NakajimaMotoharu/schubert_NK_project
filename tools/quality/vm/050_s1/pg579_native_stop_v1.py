"""SSC198 dedicated fixed resume deployment, one operator, private diagnostics only."""
import datetime,hashlib,os,pathlib,subprocess,tarfile,time,json
os.umask(0o077)
R=pathlib.Path(__file__).resolve().parent
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
classes=W/'pg579-native-tools-v1';dest='/var/lib/pgpt-s1-preservation/pg579-native-tools-v1';stage='/home/ubuntu/pg579-native-stage-v1'
assert (W/'pg579-native-compile-v1.private.log').read_bytes()==b''
opts=['-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts')]
ssh=['ssh',*opts,'-p','22222','ubuntu@127.0.0.1'];scp=['scp',*opts,'-P','22222']
assert (W/'pg579-native-oracle-v1.private.log').read_text().splitlines()[-1]=='PG579_PARENT_RECEIPT_ORACLE independentAssertions=285 nativeMutation0=true'
assert (W/'pg579-reference-oracle-v1.private.log').read_text().strip()=='PG579_REFERENCE_ORACLE independentAssertions=49 declaredVsPrimaryHistory=true all24AndOriginalsPreserved=true implicitBrokerAfterOwnedCleanupOnly=true orderedReceipts=true vmActions0=true productionPT0=true'
assert (W/'pg579-argument-oracle-v1.private.log').read_text()=='PG579_ARGUMENT_ORACLE independentAssertions=6 nullNpe0=true ownershipActions0=true\n'
subprocess.run(['python3','-B',str(R/'pg579_reference_protocol_test.py')],check=True)
subprocess.run(['python3','-B',str(R/'pg556_parent_receipt_test.py')],check=True)
subprocess.run(['python3','-B',str(R/'pg556_survivors_test.py')],check=True)
assert (W/'pg578-completed-readonly-v1.exit').read_bytes()==b'0\n'
assert not (W/'pg579-native-stop-v1.exit').exists()
files={name:classes/name for name in ['Pg579NativeStop.class','Pg579NativeStop$References.class']}
for name in ['pg579_native_refs.py','pg579_native_owned_stop.py','pg526_term_witness.py','pg526_native_term_witness.py','pg579_parent_receipt.py','pg579_durable.py']:files[name]=R/name
assert len(files)==8
bundle=P/'pg579-native-tools-v1.tar';assert not bundle.exists()
with tarfile.open(bundle,'x:') as tar:
 for name,p in sorted(files.items()):tar.add(p,arcname=name,recursive=False)
hashes={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in files.items()}
subprocess.run(ssh+['test ! -e '+stage+' && sudo -n test ! -e '+dest+' && sudo -n test ! -e /var/lib/pgpt-s1-preservation/pg579-native-stop-v1 && mkdir -m 700 '+stage],check=True)
subprocess.run(scp+[str(bundle),'ubuntu@127.0.0.1:'+stage+'/'],check=True,stdout=subprocess.DEVNULL)
payload=r'''import pathlib,os,tarfile,hashlib,stat
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
p=pathlib.Path('/home/ubuntu/pg579-native-stage-v1/pg579-native-tools-v1.tar');assert hashlib.sha256(p.read_bytes()).hexdigest()==BUNDLE
r=pathlib.Path('/var/lib/pgpt-s1-preservation/pg579-native-tools-v1');assert not r.exists();r.mkdir(mode=0o700)
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
print('PG579_STAGED fixedClassBytes=true immutable400=true starts0=true')
'''
log=W/'pg579-native-stop-v1.private.log';assert not log.exists()
with log.open('xb') as f:
 f.write((datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n').encode());f.flush()
 staged=subprocess.run(ssh+['sudo -n python3 -B -'],input=('HASHES='+repr(hashes)+'\nBUNDLE='+repr(hashlib.sha256(bundle.read_bytes()).hexdigest())+'\n'+payload).encode(),stdout=f,stderr=f);assert staged.returncode==0
 prefixes=['pg579-native-tools-v1','pg498-pending-tools-v2','pg481-pending-tools-v1','pg480-backup-tools-v3','pg477-completed-tools-v1','pg477-partial-tools-v3','pg475-readback-tools-v1','pg474-readback-tools-v1','pg473-readback-tools-v1','pg471-readback-tools-v3','pg471-completed-tools-v2','pg469-current-tools-v3','pg468-recovery-tools-v4','pg468-recovery-tools-v2','pg466-tool-v3','pg465-completed-tool-v2','pg464-completed-readback-v7','pg464-code-tools-v2','pg461-known30-tool-v3','pg456-applied-tools-v7']
 cp=':'.join('/var/lib/pgpt-s1-preservation/'+p for p in prefixes)+':/opt/schubert-nk/releases/0.1.0-PG548/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG548/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG548/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG548/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
 # Host source/static oracle is host-only; immutable guest payload pin binds the compiled result.
 began=time.monotonic()
 result=subprocess.run(ssh+['sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" Pg579NativeStop stop'],stdout=f,stderr=f)
 elapsed=time.monotonic()-began
 f.write((datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n').encode());f.flush();os.fsync(f.fileno())
with (W/'pg579-native-stop-v1.exit').open('x') as f:f.write(str(result.returncode)+'\n')
print(json.dumps({'run':'PG579-native-stop-v1','actualExit':result.returncode,'elapsedSeconds':elapsed,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest(),'oldCloseNotInferred':True,'productionPT0':True}));raise SystemExit(result.returncode)
