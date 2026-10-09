"""Independent private before/after full state; read-only original tables, no startup.
After uses immutable preimage, not the changed current to manufacture expected values.
"""
import ast,datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
from pg942_completed_sources import refs
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
def payload(mode):
    tree=ast.parse(refs());tree.body=[n for n in tree.body if not isinstance(n,ast.If)]
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='protected')
    at=next(i for i,n in enumerate(fn.body)if isinstance(n,ast.Return));fn.body[at:at]=ast.parse("value['comparison']=comparable").body
    raw=ast.unparse(ast.fix_missing_locations(tree))+'\n'
    if mode=='after':
        start=raw.index('approval_root =');end=raw.index('from pg944_parent_receipt import completed',start)
        replacement="before_path=pathlib.Path('/var/lib/pgpt-s1-preservation/pg949-publication-before-v1/after.private.json')\ns=before_path.lstat();assert stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(before_path)\nbefore_raw=before_path.read_bytes();assert before_path.lstat()==s and hashlib.sha256(before_raw).hexdigest()=='88fe076a608f8877b54bd9e250c5684fa7117667fbd952f46871382550e47d22'\nsaved=json.loads(before_raw)\nbaseline['trees']=saved['comparison']['trees']\n"
        raw=raw[:start]+replacement+raw[end:]
        marker='assert current.readlink() == old';assert raw.count(marker)==1;raw=raw.replace(marker,"assert current.readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG932')")
        raw+="SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg942-activate-v1');phase='after';expected_epoch=expected()\n"
        raw+="assert (SAVE/'complete.private').read_bytes()==b'completedDataOnly=true\\nmode=activate\\nallNewScopesReturnedNormally=true\\nold143NotNormalized=true\\ndatabaseUpdates0=true\\nstarts0=true\\n'\n"
        raw+="assert (SAVE/'old-current.private').read_bytes()==b'/opt/schubert-nk/releases/0.1.0-PG862'\nassert (SAVE/'old-approval.private').read_bytes()==b'NKRELEASEAPPROVAL1\\nversion=0.1.0-PG862\\nmanifest_sha256=20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe\\n'\nassert hashlib.sha256((SAVE/'old-epoch.private').read_bytes()).hexdigest()=='88ab94922aa165ae1c01e778521922e3693986eba93b587032affeedf16c130c'\n"
    raw+='''
def resources():
 terminal()
 for name in ('maintenance.lock','startup-admission.lock'):
  s=(pathlib.Path('/run/schubert-nk')/name).lstat()
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)<8:continue
   d=f[5].split(':');assert len(d)!=3 or(int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino)
 sql="select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;"
 assert subprocess.check_output(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],text=True).splitlines()==['0','0']
'''
    raw+="save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg949-publication-"+mode+"-v1');assert not os.path.lexists(save)\n"
    raw+='''
with StageReferences():
 resources();value=protected();assert value==protected();resources()
 save.mkdir(mode=0o700)
 with(save/'after.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 with(save/'complete.private').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(b'full24-584=true\\nfull32=true\\nretainedNativeOriginalBackup=true\\nresources0=true\\n');f.flush();os.fsync(f.fileno())
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'snapshotSha256':hashlib.sha256((save/'after.private.json').read_bytes()).hexdigest(),'full24Rows':584,'full32':True,'retainedNativeOriginalBackup':True,'allResources0':True,'rawExported':False,'formalAccepted':False}))
'''
    ast.parse(raw);return raw
if __name__=='__main__':
    os.umask(0o077);assert sys.argv[1:]in (['before'],['after']);mode=sys.argv[1]
    base=W/('pg949-publication-'+mode+'-v1');assert not Path(str(base)+'.safe.json').exists()and not Path(str(base)+'.private.log').exists()
    if mode=='after':assert json.loads((W/'pg942-activate-v1.safe.json').read_bytes())['actualExit']==0
    # Import only fixed public oracle code, not raw parent journal/credential/source data.
    receipt=(Path(__file__).parent/'pg944_parent_receipt.py').read_text();body="import sys,types\nmodule=types.ModuleType('pg944_parent_receipt');exec("+repr(receipt)+",module.__dict__);sys.modules['pg944_parent_receipt']=module\n"+payload(mode)
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    start=datetime.datetime.now(datetime.timezone.utc);r=subprocess.run(ssh,input=body.encode(),capture_output=True,timeout=60)
    with Path(str(base)+'.private.log').open('xb')as f:f.write(r.stderr);f.flush();os.fsync(f.fileno())
    safe={'actualExit':r.returncode,'mode':mode,'startedUTC':start.isoformat(),'elapsedSeconds':(datetime.datetime.now(datetime.timezone.utc)-start).total_seconds(),'privateLogSha256':hashlib.sha256(r.stderr).hexdigest(),'formalAccepted':False}
    if r.returncode==0:safe.update(json.loads(r.stdout))
    with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe));raise SystemExit(r.returncode)
