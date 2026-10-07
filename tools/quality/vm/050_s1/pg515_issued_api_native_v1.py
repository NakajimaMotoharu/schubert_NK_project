"""SSC210: fixed compiled/pinned one operator recovery. Never retry a started invocation."""
import datetime,hashlib,json,os,pathlib,shlex,subprocess,tarfile,time
os.umask(0o077)
R=pathlib.Path(__file__).resolve().parent
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
classes=W/'pg515-issued-api-tools-v3'
assert (W/'pg515-issued-api-compile-v3.private.log').read_bytes()==b''
assert (W/'pg515-issued-api-java-oracle-v3.private.log').read_text()=='PG513_SINGLE_API_ORACLE independentAssertions=20907 faultPositions=1304 realFD=true syntheticRootTmpfs=true vmActions0=true productionPT0=true\n'
assert (W/'pg515-issued-api-reference-oracle-v3.private.log').read_text()=='PG515_REFERENCE_ORACLE independentAssertions=212 orderedStopAndFault=true dependentStopNotReissued=true vmActions0=true productionPT0=true\n'
assert (W/'pg515-issued-api-broker-oracle-v3.private.log').read_text()=='PG513_BROKER_RECEIPT_ORACLE independentAssertions=48 vendorPidUidAndWholeJournal=true pid1StopDone=true vmActions0=true productionPT0=true\n'
assert (W/'pg515-issued-api-issued-oracle-v3.private.log').read_text()=='PG515_ISSUED_ORACLE independentAssertions=35102 readFaultPositions=302 transitionFaultPositions=1699 goldenCanonicalTransition=true realFD=true syntheticRootTmpfs=true vmActions0=true productionPT0=true\n'
selected=['Pg515SingleApiRecovery.class','Pg515SingleApiRecovery$References.class','dev/codex/schubert/nk/batch/file/Pg513SingleApiIntent.class','dev/codex/schubert/nk/batch/file/Pg513SingleApiIntent$Gate.class','dev/codex/schubert/nk/batch/file/Pg515IssuedApiRecovery.class']
files={name:classes/name for name in selected}
files.update({name:R/name for name in ['pg515_single_api_refs.py','pg515_confirm_ma.py']})
assert all(p.is_file() for p in files.values())
hashes={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in files.items()}
bundle=P/'pg515-issued-api-tools-v3.tar';assert not bundle.exists()
with tarfile.open(bundle,'x:') as t:
 for name,p in sorted(files.items()):t.add(p,arcname=name,recursive=False)
options=['-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts')]
ssh=['ssh',*options,'-p','22222','ubuntu@127.0.0.1'];scp=['scp',*options,'-P','22222']
stage='/home/ubuntu/pg515-issued-api-stage-v3';dest='/var/lib/pgpt-s1-preservation/pg515-issued-api-tools-v3'
subprocess.run(ssh+['test ! -e '+stage+' && sudo -n test ! -e '+dest+' && sudo -n test ! -e /var/lib/pgpt-s1-preservation/pg515-issued-api-recovery-v1 && mkdir -m 700 '+stage],check=True)
subprocess.run(scp+[str(bundle),'ubuntu@127.0.0.1:'+stage+'/'],check=True,stdout=subprocess.DEVNULL)
payload=r'''
import hashlib,os,pathlib,stat,tarfile
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
p=pathlib.Path('/home/ubuntu/pg515-issued-api-stage-v3/pg515-issued-api-tools-v3.tar');assert hashlib.sha256(p.read_bytes()).hexdigest()==BUNDLE
r=pathlib.Path('/var/lib/pgpt-s1-preservation/pg515-issued-api-tools-v3');assert not r.exists();r.mkdir(mode=0o700)
with tarfile.open(p) as t:
 names=[]
 for m in t.getmembers():
  assert m.isfile() and m.name in HASHES and '..' not in pathlib.PurePosixPath(m.name).parts and not m.name.startswith('/');names.append(m.name)
 assert len(names)==len(set(names))==len(HASHES);t.extractall(r,filter='data')
for p in r.rglob('*'):
 assert not p.is_symlink();os.chown(p,0,0)
 if p.is_dir():os.chmod(p,0o700)
 else:
  s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1;os.chmod(p,0o400)
  assert hashlib.sha256(p.read_bytes()).hexdigest()==HASHES[p.relative_to(r).as_posix()]
for p in [*reversed([p for p in r.rglob('*') if p.is_dir()]),r,r.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print('PG515_STAGED exactSevenSourceBytes=true businessActions0=true')
'''
log=W/'pg515-issued-api-native-v1.private.log';assert not log.exists()
with log.open('xb') as f:
 f.write((datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n').encode());f.flush()
 staged=subprocess.run(ssh+['sudo -n python3 -B -'],input=('HASHES='+repr(hashes)+'\nBUNDLE='+repr(hashlib.sha256(bundle.read_bytes()).hexdigest())+'\n'+payload).encode(),stdout=f,stderr=f);assert staged.returncode==0
 prefixes=['pg515-issued-api-tools-v3','pg498-pending-tools-v2','pg481-pending-tools-v1','pg480-backup-tools-v3','pg477-completed-tools-v1','pg477-partial-tools-v3','pg475-readback-tools-v1','pg474-readback-tools-v1','pg473-readback-tools-v1','pg471-readback-tools-v3','pg471-completed-tools-v2','pg469-current-tools-v3','pg468-recovery-tools-v4','pg468-recovery-tools-v2','pg466-tool-v3','pg465-completed-tool-v2','pg464-completed-readback-v7','pg464-code-tools-v2','pg461-known30-tool-v3','pg456-applied-tools-v7']
 cp=':'.join('/var/lib/pgpt-s1-preservation/'+p for p in prefixes)+':/opt/schubert-nk/releases/0.1.0-PG495/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG495/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG495/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG495/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
 began=time.monotonic()
 result=subprocess.run(ssh+['sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp '+shlex.quote(cp)+' Pg515SingleApiRecovery recover'],stdout=f,stderr=f)
 elapsed=time.monotonic()-began
 f.write(('\nNATIVE_EXIT='+str(result.returncode)+'\n').encode());f.flush();os.fsync(f.fileno())
print(json.dumps({'run':'PG515-issued-api-recovery-v1','actualExit':result.returncode,'elapsedSeconds':elapsed,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest(),'parent143NotNormalized':True,'productionPT0':True}))
raise SystemExit(result.returncode)
