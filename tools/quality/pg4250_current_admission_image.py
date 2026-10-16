"""Read-only authenticate this Root's immutable pre-start image; no replay or DB read."""
import datetime
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg4240_typed_bom_fresh_noargs_once import SLOT as ONCE
from pg4246_fresh_current_live_binding import SLOT as LIVE,SOURCE,BOM

SLOT='pg4250-current-admission-image-v1'
PUBLICATION='33b24b767326879adff27c1ee38aaa08102e347d04d631947047ef667f3352c6'


def project(value,publication):
    """Explicit field-only view; never synthesize rows, native bytes or Unit observations."""
    expected={'units','actors','database','flocks','durable','native','startup','runtime','detailedActors','configuration'}
    if type(value)is not dict or set(value)!=expected:raise ValueError('complete actual admission schema required')
    if value['actors'] or value['detailedActors'] or value['flocks'] or len(value['database']['rows'])!=24:raise ValueError('quiescent complete before required')
    if value['database']['peers'] or value['database']['locks']:raise ValueError('pre-start DB ownership must be empty')
    if sum(k.endswith('.exec')for k in value['native'])!=52:raise ValueError('all52 original streams required')
    return {'rows':value['database']['rows'],'durable':value['durable'],'oneTimeRuntime':value['runtime'],
            'configuration':value['configuration'],'unitFilesActual':publication['unitFilesActual'],'native':value['native']}


def payload(binding):
    import inspect
    return 'ONCE='+repr(ONCE)+'\nSOURCE='+repr(SOURCE)+'\nBOM='+repr(BOM)+'\nPUBLICATION='+repr(PUBLICATION)+'\nBINDING='+repr(binding)+'\n'+inspect.getsource(project)+BODY


BODY=r'''
import hashlib,json,os,pathlib,stat
require=lambda v:None if v else(_ for _ in()).throw(ValueError('actual immutable before refused'))
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip().replace('-','')==BINDING['boot'])
base=pathlib.Path('/var/lib/pgpt-s1-preservation');path=base/ONCE/'before.private.json'
def read(path):
 s=path.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(path))
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:raw=os.pread(fd,s.st_size+1,0);require(len(raw)==s.st_size and path.lstat()==s and os.fstat(fd)==s)
 finally:os.close(fd)
 require(path.read_bytes()==raw and path.lstat()==s);return raw
raw=read(path);value=json.loads(raw)
published=read(base/'pg4008-literal-invariant-publication-independent-post-v1/after.private.json');require(hashlib.sha256(published).hexdigest()==PUBLICATION)
view=project(value,json.loads(published))
manifest=pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(manifest).hexdigest()==BOM and json.loads(manifest)['source']['commit']==SOURCE)
issued=json.loads(read(base/ONCE/'external-start-issued.private.json'));require(issued['InvocationID']==BINDING['invocation']and issued['Job']==BINDING['job']and int(issued['ExecMainStartTimestampMonotonic'])==BINDING['start'])
require(read(path)==raw)
print(json.dumps({'actualExit':0,'privateBeforeSha256':hashlib.sha256(raw).hexdigest(),'tables':len(view['rows']),'nativeExecEntries':52,'publicationSha256':PUBLICATION,'rawExported':False,'liveDbReads':0,'source':SOURCE,'BOM':BOM,'binding':BINDING,'formalAccepted':False}))
'''


def live():
    v=json.loads((W/LIVE/'manifest.safe.json').read_bytes())
    if v['actualExit']!=0 or v['source']!=SOURCE:raise ValueError('actual current independent binding required')
    return {**v['result']['binding'],'rootPid':v['result']['rootPid']}


def before():
    v=json.loads((W/SLOT/'manifest.safe.json').read_bytes())
    if v['actualExit']!=0 or v['source']!=SOURCE or v['result']['binding']!=live():raise ValueError('same actual image qualification required')
    return v['result']['privateBeforeSha256']


def execute(slot,raw,timeout=60):
    from pyflakes.api import check
    if check(raw,'<complete actual admission/acceptance>'):raise ValueError('full emitted namespace static0 required')
    compile(raw,'<complete actual admission/acceptance>','exec')
    os.umask(0o077);out=W/slot;out.mkdir(mode=0o700);(out/'payload.private.py').write_text(raw)
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=timeout)
    (out/'stdout.private.log').write_bytes(r.stdout);(out/'stderr.private.log').write_bytes(r.stderr)
    v={'actualExit':r.returncode,'source':SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
    if r.returncode==0:v['result']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(v,sort_keys=True));print(json.dumps(v));return r.returncode


if __name__=='__main__':raise SystemExit(execute(SLOT,payload(live())))
