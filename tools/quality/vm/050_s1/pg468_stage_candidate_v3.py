"""BUG736: retain rejected unused RO candidate, place exact canonical new-only v3."""
import hashlib,json,pathlib,subprocess,os,sys
os.umask(0o077)
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
SOURCE='bbb244e5191e68adee2f6251dfdbbba53e9b64b4';DIGEST='8e7db782c198677015ea58572349e9748bbb19beefbd6e04afec6de1ad7630a3'
tar=P/'pg468-release-v3.tar';signature=P/'pg468-manifest-v3.sig'
opts=['-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts')]
ssh=['ssh',*opts,'-p','22222','ubuntu@127.0.0.1'];scp=['scp',*opts,'-P','22222']
subprocess.run(ssh+['umask 077; test ! -e /home/ubuntu/pg468-stage-v3 && mkdir /home/ubuntu/pg468-stage-v3'],check=True)
subprocess.run(scp+[str(tar),'ubuntu@127.0.0.1:/home/ubuntu/pg468-stage-v3/release.tar'],check=True)
payload=r'''import pathlib,hashlib,json,os,stat,subprocess,tarfile,grp
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
r=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG468');b=pathlib.Path('/var/lib/pgpt-s1-preservation');rejected=b/'pg468-rejected-release-v2';t=pathlib.Path('/home/ubuntu/pg468-stage-v3/release.tar')
assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG465')
assert not rejected.exists() and hashlib.sha256(t.read_bytes()).hexdigest()==TARHASH
assert hashlib.sha256((b/'pg468-manifest.sig').read_bytes()).hexdigest()==SIGHASH
raw=(r/'RELEASE-MANIFEST.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==DIGEST
d=json.loads(raw);assert d['source']['commit']==SOURCE and len(d['artifacts'])==186
for a in d['artifacts']:
 p=r/a['path'];assert p.stat().st_size==a['size'] and hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']
sums={a['path']:a['sha256'] for a in d['artifacts']};sums['RELEASE-MANIFEST.json']=DIGEST
canonical=''.join(sums[n]+'  '+n+'\n' for n in sorted(sums))
assert (r/'SHA256SUMS').read_text()!=canonical
for unit in ['schubert-nk-morning-controller.service','schubert-nk-api.service','schubert-nk-web.service','schubert-nk-backup.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','artemis.service','caddy.service']:
 raw=subprocess.check_output(['systemctl','show',unit,'-pMainPID','-pControlPID','-pJob','-pControlGroup'],text=True,timeout=5);fields=dict(line.split('=',1) for line in raw.splitlines());assert fields['MainPID']==fields['ControlPID']=='0' and not fields['Job']
 for f in pathlib.Path('/sys/fs/cgroup/system.slice',unit).glob('**/cgroup.procs'):assert not f.read_text().strip()
with tarfile.open(t,'r:') as a:
 names=set()
 for m in a.getmembers():
  p=pathlib.PurePosixPath(m.name);assert not p.is_absolute() and '..' not in p.parts and (m.isdir() or m.isfile()) and p.as_posix() not in names;names.add(p.as_posix())
 m=a.extractfile('./RELEASE-MANIFEST.json');assert m is not None and hashlib.sha256(m.read()).hexdigest()==DIGEST
 sumsfile=a.extractfile('./SHA256SUMS');assert sumsfile is not None and sumsfile.read()==canonical.encode('ascii')
 # Fixed never-activated candidate only; retain all rejected bytes before new extraction.
 subprocess.run(['/usr/bin/umount',str(r)],check=True,timeout=10)
 os.rename(r,rejected);r.mkdir(mode=0o750);a.extractall(r,filter='data')
group=grp.getgrnam('schubert').gr_gid
for p in [r,*r.rglob('*')]:
 st=p.lstat();assert not p.is_symlink() and (stat.S_ISDIR(st.st_mode) or (stat.S_ISREG(st.st_mode) and st.st_nlink==1))
 executable=p.relative_to(r).as_posix() in ('operations/bin/schubert-nkctl','operations/bin/schubert-nk-inbox-inspector')
 os.chown(p,0,group);os.chmod(p,0o750 if p.is_dir() or executable else 0o640)
 if p.is_file():
  with p.open('rb') as f:os.fsync(f.fileno())
assert (r/'SHA256SUMS').read_text()==canonical
for a in d['artifacts']:
 p=r/a['path'];assert p.stat().st_size==a['size'] and hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']
assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG465')
for p in [r,r.parent,b]:
 fd=os.open(p,os.O_DIRECTORY|os.O_RDONLY);os.fsync(fd);os.close(fd)
print('PG468_STAGE_V3 artifact186=true canonical187=true rejectedV1V2Retained=true signatureExact=true currentOldUnchanged=true starts0=true ddl0=true')
'''
r=subprocess.run(ssh+['sudo -n python3 -B -'],input=('SOURCE='+repr(SOURCE)+'\nDIGEST='+repr(DIGEST)+'\nTARHASH='+repr(hashlib.sha256(tar.read_bytes()).hexdigest())+'\nSIGHASH='+repr(hashlib.sha256(signature.read_bytes()).hexdigest())+'\n'+payload).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with (W/'pg468-stage-v3.private.log').open('xb') as log:log.write(r.stdout);log.write(r.stderr)
print(r.stdout.decode(),end='')
if r.returncode:print('PG468_STAGE_V3_REFUSED actual='+str(r.returncode)+' privateDiagnostics=true')
sys.exit(r.returncode)
