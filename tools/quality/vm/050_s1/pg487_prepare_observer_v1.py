"""Immutable three-file observer; latest preserved native images are not old run27."""
import hashlib,pathlib,subprocess,os
os.umask(0o077)
R=pathlib.Path(__file__).resolve().parent;W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
files={n:R/n for n in ['pg487_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py']};expected={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in files.items()}
opts=['-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts')];ssh=['ssh',*opts,'-p','22222','ubuntu@127.0.0.1'];scp=['scp',*opts,'-P','22222']
subprocess.run(ssh+['test ! -e /home/ubuntu/pg487-observer-stage-v1 && mkdir -m 700 /home/ubuntu/pg487-observer-stage-v1 && sudo -n test ! -e /var/lib/pgpt-s1-preservation/pg487-observer-v1'],check=True)
subprocess.run(scp+[*map(str,files.values()),'ubuntu@127.0.0.1:/home/ubuntu/pg487-observer-stage-v1/'],check=True,stdout=subprocess.DEVNULL)
payload=r'''import pathlib,hashlib,os,stat,json
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
root=pathlib.Path('/var/lib/pgpt-s1-preservation');save=root/'pg486-completed-codeonly';ready=save
assert (ready/'complete.private').read_bytes()==b'normalDoneCodeOnly=true\nallNewScopesReturnedNormally=true\nnewInvalidSameActivation=true\nrequestsUnchanged=true\ndatabaseUpdates0=true\nstarts0=true\n'
assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG486')
data=json.loads((save/'before.private.json').read_text())['trees']['/run/schubert-nk/pt-coverage'];count=0
for name,item in data.items():
 if item['sha256'] is None:continue
 origin=pathlib.Path(name);archive=save/'native-before-private'/origin.relative_to('/run/schubert-nk/pt-coverage');s=archive.lstat()
 assert stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1 and hashlib.sha256(archive.read_bytes()).hexdigest()==item['sha256']==hashlib.sha256(origin.read_bytes()).hexdigest();count+=1
tools=root/'pg487-observer-v1';assert not tools.exists();tools.mkdir(mode=0o700);stage=pathlib.Path('/home/ubuntu/pg487-observer-stage-v1');assert set(p.name for p in stage.iterdir())==set(EXPECTED)
for name,sha in EXPECTED.items():
 raw=(stage/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==sha
 with (tools/name).open('xb') as f:os.fchmod(f.fileno(),0o400);f.write(raw);f.flush();os.fsync(f.fileno())
for d in [tools,root]:
 fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print('PG487_OBSERVER_PREPARED immutable3=true allLatestNativeArchived=true count='+str(count)+' starts0=true')
'''
r=subprocess.run(ssh+['sudo -n python3 -B -'],input=('EXPECTED='+repr(expected)+'\n'+payload).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with (W/'pg487-observer-stage-v1.private.log').open('xb') as f:f.write(r.stdout);f.write(r.stderr)
print(r.stdout.decode(),end='');raise SystemExit(r.returncode)
