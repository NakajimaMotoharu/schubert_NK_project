"""One new-current ordinary Root, normal previous data only, original 1800s budget."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pyflakes.api import check
import pg4016_literal_invariant_current_noargs_once as old
import pg4728_ssc299_publication_post as post
import pg4734_new_current_same_peer_observer as observer
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg4434_current_candidate_admission_read import authenticate_host
from pg4188_exact_partial_recover import process

SLOT='pg4736-new-normal-root-once-v1'
SOURCE,BOM=observer.SOURCE,observer.BOM
QUALIFICATION='pg4740-new-normal-root-qualification-v1'


def action():
    raw=post.role.ro.unused.normalized_text(old.body())
    for before,after in [(old.SLOT,SLOT),('pg4012','pg4734'),('require(len(records)==46)','require(len(records)==64)'),
                         ('oldCompletedRunNotResumed','oldRunNotResumed'),('previousCompletion','previousNormalRootData')]:
        if before not in raw:raise ValueError('one exact normal once boundary '+before)
        raw=raw.replace(before,after)
    marker="persist('external-start-guard.private.json',"
    if raw.count(marker)!=1:raise ValueError('one durable reservation')
    raw=raw.replace(marker,"require(manifest_path.read_bytes()==manifest and hashlib.sha256(manifest).hexdigest()==sha)\n"+marker,1)
    raw=raw.replace("'previousNormalRootData':summary","'previousRootDataOnly':True,'previousNormalRootData':summary",1)
    return raw.replace('print(json.dumps(current))\nraise SystemExit(r.returncode)','')


def payload(hashes):
    raw=post.payload()
    marker='save=EVIDENCE'
    if raw.count(marker)!=1:raise ValueError('one output-only post boundary')
    raw=raw[:raw.index(marker)]
    if raw.count(post.SLOT)!=1:raise ValueError('one fresh prestart evidence namespace')
    raw=raw.replace(post.SLOT,SLOT+'-prestart',1)
    scopes=[n for n in ast.parse(raw).body if isinstance(n,ast.Try)and any(isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='units'for t in x.targets)for x in n.body)]
    if len(scopes)!=1:raise ValueError('one actual finite ten-reference normal admission')
    selected=scopes[0];lines=raw.splitlines(keepends=True)
    end=next(i for i in range(selected.lineno-1,selected.end_lineno)if lines[i].startswith('finally:'))
    _,summary,_=post.role.ro.unused.current_tuple()
    prelude="""parser_raw=(base/'pg477-completed-tools-v1/pg477_unit_references.py').read_bytes()
require(hashlib.sha256(parser_raw).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
parser_node=next(n for n in ast.parse(parser_raw).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record')
parser_ns={'re':re};exec(compile(ast.Module(body=[parser_node],type_ignores=[]),'<fixed actual ExecStart declaration parser>','exec'),parser_ns)
exec_record=parser_ns['exec_record']
after=expected;native=expected['native'];manifest_path=root/'RELEASE-MANIFEST.json';manifest=manifest_path.read_bytes()
def snapshot():return tree(pathlib.Path('/run/schubert-nk/pt-coverage'))
"""+'summary='+repr(summary)+'\n'
    block=prelude+action()
    result='import ast\nWATCH_FILES='+repr(hashes)+'\n'+''.join(lines[:end])+''.join(' '+s+'\n'for s in block.splitlines())+''.join(lines[end:selected.end_lineno])
    result+="\ncurrent.update(observedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),tenMetadataRefsNormalClose=True)\nprint(json.dumps(current))\nraise SystemExit(r.returncode)\n"
    if check(result,'<new normal-current once Root>'):raise ValueError('all whole emitted namespace')
    compile(result,'<new ordinary noargs once>','exec');return result


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed operator first')
    if subprocess.check_output(['git','diff','--name-only',SOURCE,'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization']):raise ValueError('same qualified source first')
    docs=['documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md','documents/300_SS/350_運用・品質/353_障害検知・復旧runbook.md']
    if subprocess.check_output(['git','diff','--ignore-blank-lines','origin/main','HEAD','--',*docs]):raise ValueError('finalized normal startup design first')
    proof=json.loads((W/'pg4730-new-current-readonly-v1/manifest.safe.json').read_bytes())
    if not(type(proof['actualExit'])is int and proof['actualExit']==0 and proof['source']==SOURCE and proof['result']['newRootNotStarted']is True and proof['result']['guestFreeBytes']>=12884901888):raise ValueError('actual new-current full readonly/capacity first')
    if not(W/'pg4734-watch-v1.started').exists()or(W/'pg4734-watch-v1.exit').exists():raise ValueError('new same-peer observer live first')
    frames=[json.loads(s)for s in(W/'pg4734-parent-watch-v1.private.jsonl').read_bytes().splitlines()]
    states=[v['states']for v in frames if 'states'in v]
    if not states or any(v['MainPID']!='0'or v['ControlPID']!='0'or v['Job']for v in states[-1].values()):raise ValueError('new independent quiescent frame first')
    hashes={n:hashlib.sha256(r.encode()).hexdigest()for n,r in observer.files().items()}
    if {p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in(P/'pg4734-observer-stage-v1').iterdir()}!=hashes:raise ValueError('complete frozen four observer files')
    raw=payload(hashes);q=json.loads((W/QUALIFICATION/'manifest.safe.json').read_bytes())
    if not(q['actualExit']==0 and q['source']==SOURCE and q['files']==hashes and q['freshOnceSha256']==hashlib.sha256(raw.encode()).hexdigest()):raise ValueError('exact whole Root qualification first')
    for name,digest in q['hostSourceHashes'].items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=digest:raise ValueError('qualified host bytes unchanged')
    authenticate_host();os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);(out/'payload.private.py').write_text(raw)
    with management_gate(P/'current-management-critical.lock'):
        with(out/'stdout.private.log').open('xb')as output,(out/'stderr.private.log').open('xb')as error:
            child=subprocess.Popen(SSH+['sudo','-n','python3','-B','-','proof'],stdin=subprocess.PIPE,stdout=output,stderr=error)
            (out/'start.safe.json').write_text(json.dumps({'owner':process(os.getpid()),'ssh':process(child.pid),'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'source':SOURCE,'replayAllowed':False}))
            child.stdin.write(raw.encode());child.stdin.close();code=child.wait();output.flush();error.flush();os.fsync(output.fileno());os.fsync(error.fileno())
    value={'actualExit':code,'source':SOURCE,'BOM':BOM,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'clientSuccessIsNotParentSuccess':True,'previousRootDataOnly':True,'formalAccepted':False}
    if code==0:value['result']=json.loads((out/'stdout.private.log').read_bytes())
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return code


if __name__=='__main__':raise SystemExit(main())
