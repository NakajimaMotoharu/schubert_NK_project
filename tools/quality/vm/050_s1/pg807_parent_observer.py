"""New807 immutable observer stage/watch, before808 one-use external same-run start."""
import ast,datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
SOURCE='102cdf1d365ab321f74b523237590eee764ae858';DIGEST='c48af3ada5e2f00b1704f65fdb4625d6220bed29b6cecbbd23d7354cf708880d'

def watch():return(R/'pg522_watch_parent.py').read_text().replace('PG495','PG796')

def files():return {'pg807_watch_parent.py':watch(),**{n:(R/n).read_text()for n in('pg457_stable_actor.py','pg462_observer_identity.py')}}

def main():
 os.umask(0o077);mode=sys.argv[1];assert mode in('stage','watch')and not subprocess.check_output(['git','status','--porcelain'])
 assert(W/'pg806-resume-post-v1.exit').read_text()=='0\n'
 opts=['-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts')];ssh=['ssh',*opts,'-p','22222','ubuntu@127.0.0.1']
 stem=W/('pg807-'+mode+'-v1');assert not any(Path(str(stem)+s).exists()for s in('.private.log','.exit','.safe.json','.started'))
 started=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with Path(str(stem)+'.started').open('x')as f:f.write(started+'\n');f.flush();os.fsync(f.fileno())
 if mode=='stage':
  bundle=P/'pg807-observer-stage-v1';assert not bundle.exists();bundle.mkdir(mode=0o700);expected={}
  for name,raw in files().items():
   ast.parse(raw)
   with(bundle/name).open('x')as f:os.fchmod(f.fileno(),0o600);f.write(raw)
   expected[name]=hashlib.sha256((bundle/name).read_bytes()).hexdigest()
  remote='/home/ubuntu/pg807-observer-stage-v1'
  with Path(str(stem)+'.private.log').open('xb')as log:
   subprocess.run(ssh+['test ! -e '+remote+' && sudo -n test ! -e /var/lib/pgpt-s1-preservation/pg807-observer-v1 && mkdir -m700 '+remote],stdout=log,stderr=log,check=True)
   subprocess.run(['scp',*opts,'-P','22222',*[str(bundle/name)for name in expected],'ubuntu@127.0.0.1:'+remote+'/'],stdout=log,stderr=log,check=True)
   payload=r'''import pathlib,hashlib,os,stat
os.umask(0o077);assert os.geteuid()==0
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG796')
assert hashlib.sha256(pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='c48af3ada5e2f00b1704f65fdb4625d6220bed29b6cecbbd23d7354cf708880d'
stage=pathlib.Path('/home/ubuntu/pg807-observer-stage-v1');root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg807-observer-v1')
assert not os.path.lexists(root)and {p.name for p in stage.iterdir()}==set(EXPECTED);root.mkdir(mode=0o700)
for name,digest in EXPECTED.items():
 raw=(stage/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==digest
 with(root/name).open('xb')as f:os.fchmod(f.fileno(),0o400);f.write(raw);f.flush();os.fsync(f.fileno())
for d in(root,root.parent):
 fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print('PG807_IMMUTABLE_OBSERVER_STAGE currentSourceVerified=true starts0=true')
'''
   result=subprocess.run(ssh+['sudo -n python3 -B -'],input=('EXPECTED='+repr(expected)+'\n'+payload).encode(),stdout=log,stderr=log);log.flush();os.fsync(log.fileno())
 else:
  assert(W/'pg807-stage-v1.exit').read_text()=='0\n'
  with(W/'pg807-parent-watch-v1.private.jsonl').open('xb')as out,Path(str(stem)+'.private.log').open('xb')as err:
   result=subprocess.run(ssh+['sudo -n python3 -B /var/lib/pgpt-s1-preservation/pg807-observer-v1/pg807_watch_parent.py '+SOURCE+' '+DIGEST+' PG796'],stdout=out,stderr=err);out.flush();os.fsync(out.fileno());err.flush();os.fsync(err.fileno())
 with Path(str(stem)+'.exit').open('x')as f:f.write(str(result.returncode)+'\n');f.flush();os.fsync(f.fileno())
 safe={'mode':mode,'actualExit':result.returncode,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':SOURCE,'privateLogSha256':hashlib.sha256(Path(str(stem)+'.private.log').read_bytes()).hexdigest(),'automaticStartStop0':True,'formalAccepted':False}
 with Path(str(stem)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
 print(json.dumps(safe));raise SystemExit(result.returncode)

if __name__=='__main__':main()
