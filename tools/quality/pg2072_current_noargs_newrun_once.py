"""One distinct ordinary noargs run after fully closed resume; full tenRefs admission, no config writes."""
import ast
import datetime
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg2070_current_newrun_observer import namespace,SOURCE,BOM
from pg2062_native_augmented_retirement_post import payload as closed_post
from pg1598_current_ordinary_once import BODY
from pg2040_fresh_normal_warning_terminal_post import SEALS

SLOT='pg2072-current-noargs-newrun-once-v1'


def body():
    raw=BODY.replace('pg1597','pg2070').replace('pg1598-current-ordinary-once-v1',SLOT)
    for old,new in [('4d6bcbddb417b76d27e52d5d9640752c300edccf',SOURCE),('e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c',BOM),('PG1544','PG1846')]:raw=raw.replace(old,new)
    raw=raw.replace('require(len(records)==10)','require(len(records)==32)').replace('>=10737418240','>=12884901888')
    old="for name,digest in WATCH_FILES.items():require(hashlib.sha256((root/name).read_bytes()).hexdigest()==digest)"
    pinned="""s=root.lstat();require(stat.S_ISDIR(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode))==(0,0,0o700)and not os.listxattr(root))
 for name,digest in WATCH_FILES.items():
  p=root/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p)and hashlib.sha256(p.read_bytes()).hexdigest()==digest)"""
    if raw.count(old)!=1:raise ValueError('one immutable observer boundary required')
    raw=raw.replace(old,pinned)
    return "declaration=exec_record(after['configuration']['schubert-nk-morning-controller.service']['ExecStart'])\nrequire(declaration is not None and not pathlib.Path('/var/lib/schubert-nk/maintenance/active').exists())\n"+raw


def payload(hashes,seals):
    raw=closed_post(seals);lines=raw.splitlines(keepends=True)
    scope=next(n for n in ast.parse(raw).body if isinstance(n,ast.Try)and any(isinstance(x,ast.FunctionDef)and x.name=='snapshot'for x in n.body))
    end=next(i for i in range(scope.lineno-1,scope.end_lineno)if lines[i].startswith('finally:'))
    action=body().replace('print(json.dumps(current))\nraise SystemExit(r.returncode)','')
    raw='WATCH_FILES='+repr(hashes)+'\n'+''.join(lines[:end])+'\n'.join('    '+line if line else line for line in action.splitlines())+'\n'+''.join(lines[end:scope.end_lineno])+"\nprint(json.dumps(current))\nraise SystemExit(r.returncode)\n"
    if check('HASHES={}\nRECEIPT="fixed"\n'+raw,'<whole current noargs newrun once>'):raise ValueError('all actual newrun globals required')
    compile(raw,'<one current ordinary newrun>','exec');return raw


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed current newrun operator required')
    prior=json.loads((W/'pg2068-retained-backup-replay-history-post-v1/manifest.safe.json').read_bytes())
    if prior['actualExit']!=0 or prior['productionSource']!=SOURCE or not prior['exactRuntimeEntryRetired']:raise ValueError('closed current retired/Backup post required')
    if not(W/'pg2070-watch-v1.started').exists()or(W/'pg2070-watch-v1.exit').exists():raise ValueError('live immutable current observer required')
    frames=[json.loads(line)for line in(W/'pg2070-parent-watch-v1.private.jsonl').read_bytes().splitlines()]
    states=[v['states']for v in frames if 'states'in v]
    if not states or any(row['MainPID']!='0'or row['ControlPID']!='0'or row['Job']for row in states[-1].values()):raise ValueError('current observer first frame must be quiescent')
    hashes={n:hashlib.sha256(s.encode()).hexdigest()for n,s in namespace()['files']().items()}
    if {p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in(P/'pg2070-observer-stage-v1').iterdir()}!=hashes:raise ValueError('immutable observer source changed')
    seals={n:prior['proofHashes'][n]['sha256']for n in SEALS}
    build=json.loads((W/'pg2051-frozen-v1.safe.json').read_bytes())
    receipt=(W/'pg2050-fresh-completed-runtime-retirement-tools-v1/pg2050_parent_receipt.py').read_text()
    raw='HASHES='+repr(build['fileHashes'])+'\nRECEIPT='+repr(receipt)+'\n'+payload(hashes,seals)
    out=W/SLOT;out.mkdir(mode=0o700);(out/'payload.private.py').write_text(raw)
    operator=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(r.stderr);(out/'stdout.private.json').write_bytes(r.stdout)
    value={'actualExit':r.returncode,'operatorSource':operator,'sourceQualified':operator==subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()and not subprocess.check_output(['git','status','--porcelain']),'productionSource':SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False,'clientSuccessIsNotParentSuccess':True,'replayForbidden':True}
    if not r.returncode:value['guest']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
