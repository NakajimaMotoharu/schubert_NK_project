"""Durable once current completed-run admission after independent full11 reauthentication."""
import ast
import datetime
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg3564_current_browser_resume_sources import SOURCE,BOM,RUN
from pg3572_current_browser_observer import namespace
import pg3570_current_browser_resume_post as post
from pg2360_current_completed_resume_once import body as proven_body

SLOT='pg3574-current-browser-resume-once-v1'


def body():
    proof=json.loads((W/post.SLOT/'manifest.safe.json').read_bytes())
    if not(proof['actualExit']==0 and proof['productionSource']==SOURCE and proof['guest']['independentResumeOnlyDeltaVerified']):
        raise ValueError('actual same-source independent prepared post required')
    raw=proven_body()
    for a,b in [('pg2358','pg3572'),('pg2360-current-completed-resume-once-v1',SLOT),
                ('3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8',SOURCE),
                ('62213f357c9dab3b00b557549426b091a03ace6557a62f4410999a02028a332c',BOM),
                ('PG2126','PG3420'),('91f5484b-9702-4c7c-97f3-dd5110a853f9',RUN),
                ('6873c5eb138bbd3dbd6a8e00398738b837dca149325db0ff555d0901bd1b10ec',proof['guest']['preparedAfterSha256']),
                ("accepted_before={**after,'configuration':dict(current_view)}",'accepted_before=after'),
                ('require(len(records)==10)','require(len(records)==28)'),
                ('hashlib.sha256(manifest).hexdigest()','hashlib.sha256(manifest.read_bytes()).hexdigest()')]:
        if a not in raw:raise ValueError('missing exact current completed-resume binding '+a[:40])
        raw=raw.replace(a,b)
    old="require(hashlib.sha256(json.dumps(native,sort_keys=True).encode()).hexdigest()=='9bf72ad074cbe798ef6082d31f25be89fe7cf3e3d31be484a997ce4b0b82c955')"
    if raw.count(old)!=1:raise ValueError('one historical native equality boundary required')
    raw=raw.replace(old,"require(native==after['native'])")
    return "def snapshot():return tree(pathlib.Path('/run/schubert-nk/pt-coverage'))\nsummary={'run':'"+RUN+"','completedOriginalOnly':True,'newActivationRequired':True}\n"+raw


def payload(hashes):
    raw=post.payload().replace(post.SLOT,SLOT)
    tree=ast.parse(raw)
    scope=next(n for n in tree.body if isinstance(n,ast.Try) and any(isinstance(x,ast.FunctionDef)and x.name=='command'for x in n.body))
    lines=raw.splitlines(keepends=True)
    end=next(i for i in range(scope.lineno-1,scope.end_lineno)if lines[i].startswith('finally:'))
    cut=next(i for i in range(scope.lineno-1,end)if lines[i]==' save.mkdir(mode=0o700)\n')
    out='WATCH_FILES='+repr(hashes)+'\n'+''.join(lines[:cut])+'\n'.join(' '+l if l else l for l in body().splitlines())+'\n'+''.join(lines[end:scope.end_lineno])+"\nprint(json.dumps(current))\nraise SystemExit(r.returncode)\n"
    if check(out,'<actual current full11 once>'):raise ValueError('complete current once globals required')
    compile(out,'<actual current durable once>','exec');return out


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed operator required')
    if subprocess.check_output(['git','diff','--name-only',SOURCE,'HEAD','--','src','pom.xml','program/characterization']):
        raise ValueError('unchanged current Main/Test/Characterization source required')
    from pg3578_current_browser_ready import require_ready
    require_ready()
    if not(W/'pg3572-watch-v1.started').exists()or(W/'pg3572-watch-v1.exit').exists():raise ValueError('live new observer required')
    frames=[json.loads(l)for l in(W/'pg3572-parent-watch-v1.private.jsonl').read_bytes().splitlines()]
    states=[f['states']for f in frames if'states'in f]
    if not states or any(v.get('race')or v['MainPID']!='0'or v['ControlPID']!='0'or v['Job']for v in states[-1].values()):
        raise ValueError('fresh stable quiescent observer frame required')
    hashes={n:hashlib.sha256(s.encode()).hexdigest()for n,s in namespace()['files']().items()}
    if {p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in(P/'pg3572-observer-stage-v1').iterdir()}!=hashes:
        raise ValueError('same staged immutable observer closure required')
    raw=payload(hashes);out=W/SLOT;out.mkdir(mode=0o700);(out/'payload.private.py').write_text(raw)
    operator=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(r.stderr);(out/'stdout.private.json').write_bytes(r.stdout)
    v={'actualExit':r.returncode,'operatorSource':operator,'productionSource':SOURCE,'sourceQualified':operator==subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()and not subprocess.check_output(['git','status','--porcelain']),'startedUTC':start,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'clientSuccessIsNotParentSuccess':True,'replayForbidden':True,'formalAccepted':False}
    if not r.returncode:v['guest']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(v,sort_keys=True));print(json.dumps(v));return r.returncode


if __name__=='__main__':raise SystemExit(main())
