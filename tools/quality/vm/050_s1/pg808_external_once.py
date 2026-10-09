"""One durable external same9de2 resume. Observer first; old native private-preserved."""
import ast,hashlib,json,os,subprocess
from pathlib import Path
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private')

PAYLOAD=r'''
import pathlib,os,sys,json,hashlib,shutil,stat,datetime,subprocess
os.umask(0o077);assert os.geteuid()==0
base=pathlib.Path('/var/lib/pgpt-s1-preservation');prep=base/'pg805-runtime-resume-v2';save=base/'pg808-external-once-v1';assert not os.path.lexists(save)
assert hashlib.sha256((prep/'complete.private').read_bytes()).hexdigest()=='479f6c1def5b869850c43bf708355a362ec6c80dd5ec5652a40627e4ba9ead80'
raw=(prep/'after.private.json').read_bytes();assert hashlib.sha256(raw).hexdigest()=='a1cd83116444d30e0ca2cb974494f0edbe30a73cd233de308c7a68a1d2f79d63';before=json.loads(raw)
sys.path.insert(0,str(base/'pg805-resume-tools-v2'));import pg805_snapshot as h
from pg777_reference_capability import CaptureReferences
h.load_definitions();assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
current=pathlib.Path('/opt/schubert-nk/current');assert str(current.readlink())==before['current']=='/opt/schubert-nk/releases/0.1.0-PG796'
manifest=(current/'RELEASE-MANIFEST.json').read_bytes();assert hashlib.sha256(manifest).hexdigest()=='c48af3ada5e2f00b1704f65fdb4625d6220bed29b6cecbbd23d7354cf708880d'and json.loads(manifest)['source']['commit']=='102cdf1d365ab321f74b523237590eee764ae858'
assert len(before['rows'])==24 and len(before['rows']['schubert.batch_runs'])==544 and len(before['unitFiles'])==18
def unchanged():
 h.parent();assert {u:h.show(u)for u in h.ORDER+h.EXTRA}==before['units']
 for u in before['units']:
  h.kernel_empty(u);assert h.complete_configuration(h.command(['/usr/bin/systemctl','show',u,'--property='+','.join(sorted(h.FIELDS_CONFIGURATION))]).decode(),u)==before['configuration'][u]
 assert h.rows()==before['rows']and {root:h.tree(pathlib.Path(root))for root in before['trees']}==before['trees']and h.tree(pathlib.Path('/run/schubert-nk/pt-coverage'))==before['coverageBefore']
 for name,value in before['unitFiles'].items():
  p=pathlib.Path(name);assert h.metadata(p)==value['metadata']and hashlib.sha256(p.read_bytes()).hexdigest()==value['sha256']and h.metadata(p)==value['metadata']
 runtime=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d');assert {p.name for p in runtime.iterdir()}=={'pg805-once-resume.conf'}
 s=(runtime/'pg805-once-resume.conf').lstat();assert stat.S_ISREG(s.st_mode)and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o644 and s.st_nlink==1
 assert hashlib.sha256((runtime/'pg805-once-resume.conf').read_bytes()).hexdigest()=='eb600f61cdc75089d2cc66da426ff69efe8b644806e8b21684ae5ebc88466911'
 q="select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;"
 assert h.command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines()==[b'0',b'0']
 for name in('maintenance.lock','startup-admission.lock'):
  s=pathlib.Path('/run/schubert-nk',name).lstat()
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)<8:continue
   d=f[5].split(':');assert len(d)!=3 or(int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino)
def persist(name,value):
 with(save/name).open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
with CaptureReferences():
 unchanged();unchanged();save.mkdir(mode=0o700)
 native=pathlib.Path('/run/schubert-nk/pt-coverage');shutil.copytree(native,save/'native-before',symlinks=False)
 for p in(save/'native-before',*(save/'native-before').rglob('*')):
  assert not p.is_symlink()
  if p.is_file():
   os.chmod(p,0o600)
   with p.open('rb')as f:os.fsync(f.fileno())
  elif p.is_dir():os.chmod(p,0o700)
  else:raise ValueError('unknown private native entry')
 unchanged()
 active=pathlib.Path('/var/lib/schubert-nk/maintenance/active').read_bytes().decode('ascii').splitlines();assert len(active)==4 and active[0]=='NKACT1'and active[1]=='9de2d03c-28c7-4647-97d9-c66ace06048c'and active[2]=='2026-10-09T05:42:22.532331Z'
 persist('external-start-guard.private.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':'102cdf1d365ab321f74b523237590eee764ae858','manifestSha256':'c48af3ada5e2f00b1704f65fdb4625d6220bed29b6cecbbd23d7354cf708880d','run':active[1],'cutoff':active[2],'originalBudgetSeconds':1800,'attemptReserved':True,'repeatForbidden':True})
 r=subprocess.run(['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=15)
 raw=subprocess.check_output(['/usr/bin/systemctl','show','schubert-nk-morning-controller.service','--property=InvocationID,MainPID,Job,ExecMainStartTimestampMonotonic'],text=True,timeout=5);values=dict(line.split('=',1)for line in raw.splitlines());values.update(clientExit=r.returncode,at=datetime.datetime.now(datetime.timezone.utc).isoformat(),clientSuccessIsNotParentSuccess=True)
 persist('external-start-issued.private.json',values)
print(json.dumps(values));raise SystemExit(r.returncode)
'''

def main():
 os.umask(0o077);assert not subprocess.check_output(['git','status','--porcelain']);assert(W/'pg806-resume-post-v1.exit').read_text()=='0\n'
 assert(W/'pg807-watch-v1.started').exists()and not(W/'pg807-watch-v1.exit').exists();watch=W/'pg807-parent-watch-v1.private.jsonl';assert watch.exists()and watch.stat().st_size>0
 base=W/'pg808-external-once-v1';assert not any(Path(str(base)+s).exists()for s in('.private.log','.safe.json','.exit'))
 ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -'];ast.parse(PAYLOAD)
 with Path(str(base)+'.private.log').open('xb')as f:r=subprocess.run(ssh,input=PAYLOAD.encode(),stdout=subprocess.PIPE,stderr=f);f.flush();os.fsync(f.fileno())
 with Path(str(base)+'.exit').open('x')as f:f.write(str(r.returncode)+'\n')
 if r.returncode==0:
  safe=json.loads(r.stdout);safe.update(operatorSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),privateLogSha256=hashlib.sha256(Path(str(base)+'.private.log').read_bytes()).hexdigest(),formalAccepted=False)
  with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
  print(json.dumps(safe))
 else:print(json.dumps({'actualExit':r.returncode,'privateErrorSha256':hashlib.sha256(Path(str(base)+'.private.log').read_bytes()).hexdigest(),'priorReservationMustBeChecked':True}))
 raise SystemExit(r.returncode)

if __name__=='__main__':main()
