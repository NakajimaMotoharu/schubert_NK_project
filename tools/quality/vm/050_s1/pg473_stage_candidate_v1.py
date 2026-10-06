"""Place new-only verified unused PG473; current/services/DB/startup remain untouched."""
import hashlib,json,pathlib,subprocess,os
os.umask(0o077)
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
SOURCE='a5f9e6a54427ff356626245230496d8667082465'
DIGEST='ffae42347b43d9654d026f66f10cbf81ce9a98baa30bb33510ff19279d90676d'
release=W/'pg473-release-v1';tar=P/'pg473-release.tar';sig=P/'pg473-manifest-v1.sig'
assert not tar.exists() and not (W/'pg473-candidate-stage-v1.private.log').exists()
raw=(release/'RELEASE-MANIFEST.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==DIGEST
data=json.loads(raw);assert data['source']['commit']==SOURCE and len(data['artifacts'])==186
for a in data['artifacts']:
 p=release/a['path'];assert p.stat().st_size==a['size'] and hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']
subprocess.run(['tar','-C',str(release),'-cf',str(tar),'.'],check=True)
opts=['-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts')]
ssh=['ssh',*opts,'-p','22222','ubuntu@127.0.0.1'];scp=['scp',*opts,'-P','22222']
subprocess.run(ssh+['test ! -e /home/ubuntu/pg473-stage && sudo -n test ! -e /opt/schubert-nk/releases/0.1.0-PG473 && sudo -n test ! -e /var/lib/pgpt-s1-preservation/pg473-manifest.sig && mkdir -m 700 /home/ubuntu/pg473-stage'],check=True)
subprocess.run(scp+[str(tar),str(sig),'ubuntu@127.0.0.1:/home/ubuntu/pg473-stage/'],check=True)
payload=r'''import os,pathlib,hashlib,json,tarfile,stat,grp,subprocess
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
current=pathlib.Path('/opt/schubert-nk/current');old=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG472');assert current.readlink()==old
r=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG473');s=pathlib.Path('/home/ubuntu/pg473-stage');dest=pathlib.Path('/var/lib/pgpt-s1-preservation/pg473-manifest.sig')
assert not r.exists() and not r.is_symlink() and not dest.exists() and not dest.is_symlink()
assert hashlib.sha256((s/'pg473-release.tar').read_bytes()).hexdigest()==TARHASH
signature=(s/'pg473-manifest-v1.sig').read_bytes();assert len(signature)==64 and hashlib.sha256(signature).hexdigest()==SIGHASH
with tarfile.open(s/'pg473-release.tar','r:') as archive:
 names=set()
 for m in archive.getmembers():
  p=pathlib.PurePosixPath(m.name);assert not p.is_absolute() and '..' not in p.parts and (m.isdir() or m.isfile()) and p.as_posix() not in names;names.add(p.as_posix())
 raw=archive.extractfile('./RELEASE-MANIFEST.json').read();assert hashlib.sha256(raw).hexdigest()==DIGEST
 data=json.loads(raw);assert data['source']['commit']==SOURCE and len(data['artifacts'])==186
 sums={a['path']:a['sha256'] for a in data['artifacts']};sums['RELEASE-MANIFEST.json']=DIGEST
 canonical=''.join(sums[n]+'  '+n+'\n' for n in sorted(sums));assert archive.extractfile('./SHA256SUMS').read()==canonical.encode('ascii')
 r.mkdir(mode=0o750);archive.extractall(r,filter='data')
group=grp.getgrnam('schubert').gr_gid
for p in [r,*r.rglob('*')]:
 st=p.lstat();assert not p.is_symlink() and (stat.S_ISDIR(st.st_mode) or (stat.S_ISREG(st.st_mode) and st.st_nlink==1))
 executable=p.relative_to(r).as_posix() in ('operations/bin/schubert-nkctl','operations/bin/schubert-nk-inbox-inspector')
 os.chown(p,0,group);os.chmod(p,0o750 if p.is_dir() or executable else 0o640)
 if p.is_file():
  with p.open('rb') as f:os.fsync(f.fileno())
for a in data['artifacts']:
 p=r/a['path'];assert p.stat().st_size==a['size'] and hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']
assert (r/'SHA256SUMS').read_text()==canonical
with dest.open('xb') as f:os.fchmod(f.fileno(),0o400);f.write(signature);f.flush();os.fsync(f.fileno())
subprocess.run(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(r/'RELEASE-MANIFEST.json'),'-sigfile',str(dest)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
assert current.readlink()==old
for p in [r,r.parent,dest.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print('PG473_CANDIDATE_PLACED artifacts186=true canonical187=true signatureVerified=true oldCurrentUnchanged=true starts0=true stops0=true ddl0=true')
'''
run=subprocess.run(ssh+['sudo -n python3 -B -'],input=('SOURCE='+repr(SOURCE)+'\nDIGEST='+repr(DIGEST)+'\nTARHASH='+repr(hashlib.sha256(tar.read_bytes()).hexdigest())+'\nSIGHASH='+repr(hashlib.sha256(sig.read_bytes()).hexdigest())+'\n'+payload).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with (W/'pg473-candidate-stage-v1.private.log').open('xb') as f:f.write(run.stdout);f.write(run.stderr)
print(run.stdout.decode(),end='')
if run.returncode:print('PG473_CANDIDATE_REFUSED actual='+str(run.returncode)+' privateDiagnostics=true partialCandidateRetained=true')
raise SystemExit(run.returncode)
