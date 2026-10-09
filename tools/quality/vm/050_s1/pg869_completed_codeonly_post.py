"""Independent current862 full post; exact old861 plus finite new epoch/approval only."""
import ast,datetime,hashlib,json,os,subprocess
from pathlib import Path
from pg864_completed_sources import refs
from pg864_compile_v3 import profile_v3
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
def payload():
    raw=profile_v3(refs());tree=ast.parse(raw)
    tree.body=[n for n in tree.body if not isinstance(n,ast.If)]
    raw=ast.unparse(tree)+'\n'
    old='assert current.readlink() == old';assert raw.count(old)==1
    raw=raw.replace(old,"assert current.readlink() == pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG862')")
    raw+='''
save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg869-current862-post-v1');assert not os.path.lexists(save)
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg864-activate-v3');phase='after';expected_epoch=expected()
assert (SAVE/'complete.private').read_bytes()==b'completedDataOnly=true\\nmode=activate\\nallNewScopesReturnedNormally=true\\nold143NotNormalized=true\\ndatabaseUpdates0=true\\nstarts0=true\\n'
assert (SAVE/'old-current.private').read_bytes()==b'/opt/schubert-nk/releases/0.1.0-PG832'
assert hashlib.sha256((SAVE/'old-epoch.private').read_bytes()).hexdigest()==baseline['trees']['/run/schubert-nk/startup']['/run/schubert-nk/startup/epoch.current']['sha256']
assert hashlib.sha256((SAVE/'old-approval.private').read_bytes()).hexdigest()==baseline['trees']['/etc/schubert-nk/release-approval']['/etc/schubert-nk/release-approval/current']['sha256']
candidate=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG862');bom=(candidate/'RELEASE-MANIFEST.json').read_bytes()
assert hashlib.sha256(bom).hexdigest()=='20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe'
data=json.loads(bom);assert data['source']['commit']=='e01612fcd7f2752df5ae0836b78538fd5e87f120' and len(data['artifacts'])==187 and len(data['migrations'])==29 and data['versions']['schema']=='028'
for r in data['artifacts']:
 p=candidate/r['path'];assert p.stat().st_size==r['size']and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
subprocess.run(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(candidate/'RELEASE-MANIFEST.json'),'-sigfile','/var/lib/pgpt-s1-preservation/pg862-manifest.sig'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def resources():
 terminal()
 for name in ('maintenance.lock','startup-admission.lock'):
  s=(pathlib.Path('/run/schubert-nk')/name).lstat()
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)<8:continue
   d=f[5].split(':');assert len(d)!=3 or (int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino)
 q="select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;"
 assert subprocess.check_output(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],text=True).splitlines()==['0','0']
with StageReferences():
 resources();value=protected();assert value==protected();resources()
 save.mkdir(mode=0o700)
 with (save/'after.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 with (save/'complete.private').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(b'independentCurrent862=true\\noriginalDONEPreserved=true\\noldParent143Preserved=true\\nfull24Unchanged=true\\nresources0=true\\n');f.flush();os.fsync(f.fileno())
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'current862':True,'productionSource':'e01612fcd7f2752df5ae0836b78538fd5e87f120','oldParent143Preserved':True,'originalDONEPreserved':True,'full24Rows':564,'startupEntries':47,'full32':True,'runtimeEmpty':True,'allResources0':True,'snapshotSha256':hashlib.sha256((save/'after.private.json').read_bytes()).hexdigest(),'completeSha256':hashlib.sha256((save/'complete.private').read_bytes()).hexdigest(),'newEpochSha256':hashlib.sha256(expected_epoch).hexdigest(),'formalAccepted':False}))
'''
    ast.parse(raw);return raw
if __name__=='__main__':
    os.umask(0o077);assert json.loads((W/'pg864-activate-v3.safe.json').read_bytes())['actualExit']==0
    base=W/'pg869-current862-post-v1';assert not Path(str(base)+'.private.log').exists()
    cmd=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    start=datetime.datetime.now(datetime.timezone.utc);result=subprocess.run(cmd,input=payload().encode(),capture_output=True)
    with Path(str(base)+'.private.log').open('xb')as f:f.write(result.stderr);f.flush();os.fsync(f.fileno())
    safe={'run':'PG869-current862-post-v1','actualExit':result.returncode,'startedUTC':start.isoformat(),'elapsedSeconds':(datetime.datetime.now(datetime.timezone.utc)-start).total_seconds(),'privateLogSha256':hashlib.sha256(result.stderr).hexdigest(),'formalAccepted':False}
    if result.returncode==0:safe.update(json.loads(result.stdout))
    with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,indent=2);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe));raise SystemExit(result.returncode)
