"""SSC206 new-only immutable tools, one cold preparation. Private logs; no business starts."""
import datetime,hashlib,json,os,pathlib,subprocess,tarfile
os.umask(0o077)
R=pathlib.Path(__file__).resolve().parent
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
classes=W/'pg502-cold-tools-v1'
options=['-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts')]
ssh=['ssh',*options,'-p','22222','ubuntu@127.0.0.1'];scp=['scp',*options,'-P','22222']
assert (W/'pg502-cold-compile-v1.private.log').read_bytes()==b''
assert (W/'pg502-cold-oracle-v1.private.log').read_text()=='PG502_COLD_ORACLE independentAssertions=76 productionPT0=true nativeMutation0=true\n'
assert (W/'pg502-db-oracle-v1.private.log').read_text()=='PG502_DB_ORACLE independentAssertions=16 rejectedModes=5 readonlyStatement0=true parentLifecycleCalls0=true actualDB0=true\n'
files={p.name:p for p in classes.glob('Pg502ColdPreparation*.class')};files['pg502_cold_refs.py']=R/'pg502_cold_refs.py';assert len(files)==3
hashes={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in files.items()}
bundle=P/'pg502-cold-tools-v1.tar';assert not bundle.exists()
with tarfile.open(bundle,'x:') as t:
 for name,p in sorted(files.items()):t.add(p,arcname=name,recursive=False)
stage='/home/ubuntu/pg502-cold-stage-v1';destination='/var/lib/pgpt-s1-preservation/pg502-cold-tools-v1'
subprocess.run(ssh+['test ! -e '+stage+' && sudo -n test ! -e '+destination+' && sudo -n test ! -e /var/lib/pgpt-s1-preservation/pg502-cold-preparation-v1 && mkdir -m 700 '+stage],check=True)
subprocess.run(scp+[str(bundle),'ubuntu@127.0.0.1:'+stage+'/'],check=True,stdout=subprocess.DEVNULL)
payload=r'''
import os,pathlib,hashlib,tarfile,stat
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
p=pathlib.Path('/home/ubuntu/pg502-cold-stage-v1/pg502-cold-tools-v1.tar');assert hashlib.sha256(p.read_bytes()).hexdigest()==BUNDLE
r=pathlib.Path('/var/lib/pgpt-s1-preservation/pg502-cold-tools-v1');assert not r.exists();r.mkdir(mode=0o700)
with tarfile.open(p) as t:
 names=[]
 for m in t.getmembers():
  assert m.isfile() and m.name in HASHES and '/' not in m.name;names.append(m.name)
 assert len(names)==len(set(names))==len(HASHES);t.extractall(r,filter='data')
for p in r.iterdir():
 s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1;os.chown(p,0,0);os.chmod(p,0o400)
 assert hashlib.sha256(p.read_bytes()).hexdigest()==HASHES[p.name]
for p in [r,r.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print('PG502_STAGED immutableSourceBytes=true businessActions=0')
'''
log=W/'pg502-cold-native-v1.private.log';assert not log.exists()
with log.open('xb') as f:
 f.write((datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n').encode());f.flush()
 staged=subprocess.run(ssh+['sudo -n python3 -B -'],input=('HASHES='+repr(hashes)+'\nBUNDLE='+repr(hashlib.sha256(bundle.read_bytes()).hexdigest())+'\n'+payload).encode(),stdout=f,stderr=f)
 assert staged.returncode==0
 prefixes=['pg502-cold-tools-v1','pg498-pending-tools-v2','pg481-pending-tools-v1','pg480-backup-tools-v3','pg477-completed-tools-v1','pg477-partial-tools-v3','pg475-readback-tools-v1','pg474-readback-tools-v1','pg473-readback-tools-v1','pg471-readback-tools-v3','pg471-completed-tools-v2','pg469-current-tools-v3','pg468-recovery-tools-v4','pg468-recovery-tools-v2','pg466-tool-v3','pg465-completed-tool-v2','pg464-completed-readback-v7','pg464-code-tools-v2','pg461-known30-tool-v3','pg456-applied-tools-v7']
 cp=':'.join('/var/lib/pgpt-s1-preservation/'+p for p in prefixes)+':/opt/schubert-nk/releases/0.1.0-PG495/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG495/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG495/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG495/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
 result=subprocess.run(ssh+['sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" Pg502ColdPreparation prepare'],stdout=f,stderr=f)
 f.write((datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n').encode());f.flush();os.fsync(f.fileno())
with (W/'pg502-cold-native-v1.exit').open('x') as f:f.write(str(result.returncode)+'\n')
print(json.dumps({'id':'PG502-cold-native-v1','exitCode':result.returncode,'oldRuntimeRetirementNotInferred':True,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest()}))
raise SystemExit(result.returncode)
