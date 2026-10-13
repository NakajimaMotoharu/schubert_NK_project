"""One external fresh activation for a completed run; continuous ten Ref, no config writes."""
import ast
import datetime
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg2010_fresh_completed_resume_observer import namespace,SOURCE,BOM
from pg2013_online_capacity_independent_post import payload as preflight
from pg1598_current_ordinary_once import BODY

SLOT='pg2015-completed-run-fresh-resume-once-v1'
RUN='4148e3e8-f107-431a-ab27-d6e6d1f1772e'


def body():
    raw=BODY.replace('pg1597','pg2010').replace('pg1598-current-ordinary-once-v1',SLOT)
    raw=raw.replace('4d6bcbddb417b76d27e52d5d9640752c300edccf',SOURCE).replace('e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c',BOM).replace('PG1544','PG1846')
    old="require(native==after['native']and declaration[1].endswith('dev.codex.schubert.nk.batch.file.MorningProcessMain')and '--resume'not in declaration[1])"
    new="""declaration=exec_record(after['configuration']['schubert-nk-morning-controller.service']['ExecStart'])
require(declaration is not None and declaration[1].endswith('dev.codex.schubert.nk.batch.file.MorningProcessMain --resume 4148e3e8-f107-431a-ab27-d6e6d1f1772e'))
require(hashlib.sha256(json.dumps(after,sort_keys=True).encode()).hexdigest()=='fd6412f31de9af59219a0fe28f49ce0d073b074a7ff83ca3516a22e462568b83')
require(hashlib.sha256(json.dumps(native,sort_keys=True).encode()).hexdigest()=='b9dce89b8ab71f077937a4eb2fd87141d5e7e3dcf300e3614080d42fd51a2683')
require(not pathlib.Path('/var/lib/schubert-nk/maintenance/active').exists())"""
    if raw.count(old)!=1:raise ValueError('one noargs admission boundary required')
    raw=raw.replace(old,new).replace('>=10737418240','>=12884901888').replace('require(len(records)==10)','require(len(records)==26)')
    raw=raw.replace('ordinaryNoargs','freshCompletedRunResume').replace('oldCompletedRunNotResumed','newActivationByProduction').replace("'previousCompletion':summary","'previousCompletion':summary,'selectedRun':'"+RUN+"'")
    raw=raw.replace("print(json.dumps(current))\nraise SystemExit(r.returncode)","")
    # Staged files are immutable, root-owned, single-link, no ACL; never an arbitrary script.
    old="for name,digest in WATCH_FILES.items():require(hashlib.sha256((root/name).read_bytes()).hexdigest()==digest)"
    new="""s=root.lstat();require(stat.S_ISDIR(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode))==(0,0,0o700)and not os.listxattr(root))
 for name,digest in WATCH_FILES.items():
  p=root/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p)and hashlib.sha256(p.read_bytes()).hexdigest()==digest)"""
    if raw.count(old)!=1:raise ValueError('one immutable observer file boundary required')
    return raw.replace(old,new)


def payload(hashes):
    raw=preflight();lines=raw.splitlines(keepends=True)
    scope=next(n for n in ast.parse(raw).body if isinstance(n,ast.Try)and any(isinstance(x,ast.FunctionDef)and x.name=='snapshot'for x in n.body))
    end=next(i for i in range(scope.lineno-1,scope.end_lineno)if lines[i].startswith('finally:'))
    capacity=raw[raw.index("require(pathlib.Path('/proc/sys/kernel/random/boot_id')",raw.index('finally:')):raw.index("save=base/'pg2013-online-capacity-independent-post-v1'")]
    raw='WATCH_FILES='+repr(hashes)+'\n'+''.join(lines[:end])+'\n'.join('    '+line if line else line for line in (capacity+body()).splitlines())+'\n'+''.join(lines[end:scope.end_lineno])+"\nprint(json.dumps(current))\nraise SystemExit(r.returncode)\n"
    from pyflakes.api import check
    if check(raw,'<actual fresh completed resume once>'):raise ValueError('all once globals required')
    compile(raw,'<one external fresh activation continuous ten Ref>','exec');return raw


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed operator required')
    prior=json.loads((W/'pg2013-online-capacity-independent-post-v1/manifest.safe.json').read_bytes())
    if prior['actualExit']!=0 or prior['allClientAdvisoryFlock0']is not True or prior['productionSource']!=SOURCE:raise ValueError('current closed independent fullpost required')
    if not(W/'pg2010-watch-v1.started').exists()or(W/'pg2010-watch-v1.exit').exists():raise ValueError('current live observer required')
    frames=[json.loads(line)for line in (W/'pg2010-parent-watch-v1.private.jsonl').read_bytes().splitlines()]
    states=[frame['states']for frame in frames if 'states'in frame]
    if not states or any(row['MainPID']!='0'or row['ControlPID']!='0'or row['Job']for row in states[-1].values()):raise ValueError('new observer quiescent first frame required')
    expected={n:hashlib.sha256(s.encode()).hexdigest()for n,s in namespace()['files']().items()}
    if {p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in(P/'pg2010-observer-stage-v1').iterdir()}!=expected:raise ValueError('fixed observer source changed')
    out=W/SLOT;out.mkdir(mode=0o700);raw=payload(expected);(out/'payload.private.py').write_text(raw)
    operator=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(r.stderr);(out/'stdout.private.json').write_bytes(r.stdout)
    value={'actualExit':r.returncode,'operatorSource':operator,'sourceQualified':operator==subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()and not subprocess.check_output(['git','status','--porcelain']),'productionSource':SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False,'clientSuccessIsNotParentSuccess':True,'replayForbidden':True}
    if not r.returncode:value['guest']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
