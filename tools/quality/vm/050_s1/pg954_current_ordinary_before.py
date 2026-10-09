"""New40ef canonical noargs before: old static Unit file bytes are oracle data only."""
import ast,datetime,hashlib,inspect,json,os,subprocess,types
from pathlib import Path
from pg949_publication_snapshot import payload as current_payload
from pg870_ordinary_before import parser_source,EXTRA as old_extra
from pg870_ordinary_policy import ordinary_argv
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
def prefix():
    code=(Path(__file__).parent/'pg944_parent_receipt.py').read_text()
    return "import sys,types\nmodule=types.ModuleType('pg944_parent_receipt');exec("+repr(code)+",module.__dict__);sys.modules['pg944_parent_receipt']=module\n"
def definitions():
    raw=current_payload('after');raw=raw[:raw.index("save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg949-publication-after-v1')")]
    raw+='''
static_raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg870-ordinary-before-v1/after.private.json').read_bytes()
assert hashlib.sha256(static_raw).hexdigest()=='a8c6c5d4dca5c02b1ae6b3ee797ba87d129b0dc4851ae31f6e7609ebfd31d980'
static_units=json.loads(static_raw)['unitFiles'];assert len(static_units)==18
baseline['unitFiles']=static_units
candidate=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG932')
assert hashlib.sha256((candidate/'RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524'
assert os.statvfs(candidate).f_flag&os.ST_RDONLY
'''
    extra=old_extra.replace("'oldParent143NotAccepted':True","'oldParent143NotAccepted':True,'oldGenuineRootPreserved':True,'source':'40ef6e894573d2ffab1d1732124960f9c98d5f97'")
    raw+=inspect.getsource(ordinary_argv)+'\n'+parser_source()+'\n'+extra
    ast.parse(raw);return raw
def payload():
    raw=definitions()+"\nsave=pathlib.Path('/var/lib/pgpt-s1-preservation/pg954-ordinary-before-v1');assert not os.path.lexists(save)\n"
    raw+='''
with StageReferences():
 resources();limited=protected();assert limited==protected();resources()
 original=pathlib.Path('/var/lib/pgpt-s1-preservation/pg949-publication-after-v1/after.private.json').read_bytes()
 assert hashlib.sha256(original).hexdigest()=='8b44b0db4a95049cc9d2085964d6538df428e3ada13877f8d07c47f711fa39f0'
 assert limited==json.loads(original)
 value=standard_snapshot(limited);assert value==standard_snapshot(protected())
 save.mkdir(mode=0o700)
 with(save/'after.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'source':'40ef6e894573d2ffab1d1732124960f9c98d5f97','beforeSha256':hashlib.sha256((save/'after.private.json').read_bytes()).hexdigest(),'ordinaryNoargs':True,'oldCompletedNotResumed':True,'unitFiles':len(value['unitFiles']),'full24Rows':len(value['rows']['schubert.batch_runs']),'full32':True,'nativeBeforeCount':len(value['coverageBefore']),'starts0':True,'formalAccepted':False}))
'''
    ast.parse(raw);return prefix()+raw
if __name__=='__main__':
    os.umask(0o077);assert not subprocess.check_output(['git','status','--porcelain']);base=W/'pg954-ordinary-before-v1'
    assert not Path(str(base)+'.safe.json').exists()and not Path(str(base)+'.private.log').exists()
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    start=datetime.datetime.now(datetime.timezone.utc);r=subprocess.run(ssh,input=payload().encode(),capture_output=True,timeout=60)
    with Path(str(base)+'.private.log').open('xb')as f:f.write(r.stderr);f.flush();os.fsync(f.fileno())
    safe={'actualExit':r.returncode,'startedUTC':start.isoformat(),'elapsedSeconds':(datetime.datetime.now(datetime.timezone.utc)-start).total_seconds(),'privateLogSha256':hashlib.sha256(r.stderr).hexdigest(),'formalAccepted':False}
    if r.returncode==0:safe.update(json.loads(r.stdout))
    with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe));raise SystemExit(r.returncode)
