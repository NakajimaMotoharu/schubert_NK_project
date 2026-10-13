"""One new-source noargs acceptance run after normal publication, no replay."""
import ast
import datetime
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg1598_current_ordinary_once import BODY
from pg2176_newsource_normal_observer import namespace,SOURCE,BOM
from pg2174_normal_publication_post import payload as full_post

SLOT='pg2178-newsource-noargs-once-v1'


def body():
    raw=BODY
    for old,new in [('pg1597','pg2176'),('pg1598-current-ordinary-once-v1',SLOT),('4d6bcbddb417b76d27e52d5d9640752c300edccf',SOURCE),('e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c',BOM),('PG1544','PG2126'),('require(len(records)==10)','require(len(records)==38)'),('>=10737418240','>=12884901888')]:raw=raw.replace(old,new)
    old="for name,digest in WATCH_FILES.items():require(hashlib.sha256((root/name).read_bytes()).hexdigest()==digest)"
    new="""s=root.lstat();require(stat.S_ISDIR(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode))==(0,0,0o700)and not os.listxattr(root))
 for name,digest in WATCH_FILES.items():
  p=root/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p)and hashlib.sha256(p.read_bytes()).hexdigest()==digest)"""
    if raw.count(old)!=1:raise ValueError('one actual immutable observer boundary required')
    raw=raw.replace(old,new)
    return "declaration=exec_record(after['configuration']['schubert-nk-morning-controller.service']['ExecStart'])\nrequire(declaration is not None and not pathlib.Path('/var/lib/schubert-nk/maintenance/active').exists())\n"+raw


def payload(hashes):
    raw=full_post();raw=raw[:raw.index("save=base/'pg2174-normal-publication-full-post-v1'")]
    # Reuse complete qualified verifier, replacing only the last reader scope with
    # a new current read-only scope that retains all ten references during start.
    lines=raw.splitlines(keepends=True)
    scopes=[n for n in ast.parse(raw).body if isinstance(n,ast.Try)and any(isinstance(x,ast.FunctionDef)and x.name=='snapshot'for x in n.body)]
    if len(scopes)!=1:raise ValueError('one independent ten-reference admission scope required')
    scope=scopes[0];end=next(i for i in range(scope.lineno-1,scope.end_lineno)if lines[i].startswith('finally:'))
    action=body().replace('print(json.dumps(current))\nraise SystemExit(r.returncode)','')
    prefix='WATCH_FILES='+repr(hashes)+'\n'+''.join(lines[:end])
    # Do not claim old native was produced by new Main. Preserve it verbatim only.
    prefix+='''    parser_raw=(base/'pg477-completed-tools-v1/pg477_unit_references.py').read_bytes()
    require(hashlib.sha256(parser_raw).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
    parser_node=next(n for n in ast.parse(parser_raw).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record')
    parser_ns={'re':re};exec(compile(ast.Module(body=[parser_node],type_ignores=[]),'<fixed actual ExecStart declaration parser>','exec'),parser_ns)
    exec_record=parser_ns['exec_record']
    after={**after,'native':native}
'''
    raw=prefix+'\n'.join('    '+line if line else line for line in action.splitlines())+'\n'+''.join(lines[end:scope.end_lineno])+"\nprint(json.dumps(current))\nraise SystemExit(r.returncode)\n"
    from pyflakes.api import check
    if check(raw,'<actual newsource noargs once>'):raise ValueError('whole actual globals required')
    compile(raw,'<actual newsource noargs once>','exec');return raw


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('fixed clean current noargs operator required')
    post=json.loads((W/'pg2174-normal-publication-full-post-v1/manifest.safe.json').read_bytes())
    if post['actualExit']!=0 or post['guest']['productionSource']!=SOURCE or post['guest']['unitExchangeAndReload']is not False:
        raise ValueError('actual current normal source/unchanged Unit required')
    if not(W/'pg2176-watch-v1.started').exists()or(W/'pg2176-watch-v1.exit').exists():raise ValueError('live current immutable observer required')
    frames=[json.loads(line)for line in(W/'pg2176-parent-watch-v1.private.jsonl').read_bytes().splitlines()]
    states=[v['states']for v in frames if 'states'in v]
    if not states or any(v['MainPID']!='0'or v['ControlPID']!='0'or v['Job']for v in states[-1].values()):raise ValueError('new current quiescent first frame required')
    hashes={n:hashlib.sha256(s.encode()).hexdigest()for n,s in namespace()['files']().items()}
    if {p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in(P/'pg2176-observer-stage-v1').iterdir()}!=hashes:raise ValueError('immutable observer bytes changed')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload(hashes).encode();(out/'payload.private.py').write_bytes(raw)
    operator=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw,capture_output=True,timeout=120)
    (out/'stderr.private.log').write_bytes(r.stderr);(out/'stdout.private.json').write_bytes(r.stdout)
    v={'actualExit':r.returncode,'operatorSource':operator,'sourceQualified':operator==subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'productionSource':SOURCE,'payloadSha256':hashlib.sha256(raw).hexdigest(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False,'clientSuccessIsNotParentSuccess':True,'replayForbidden':True}
    if not r.returncode:v['guest']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(v,sort_keys=True));print(json.dumps(v));return r.returncode


if __name__=='__main__':raise SystemExit(main())
