"""SSC291 new-only six-unit driver; inherit qualified declaration/pool fixes, not old partial actions."""
import ast
import base64
import hashlib
import inspect
import json
import os
import subprocess
import sys
from pyflakes.api import check
import pg4312_current_failed_owned_sources as role
import pg4304_current_failed_parent_contract as parent
import pg4166_partial_recovery_sources as predecessor
from pg4060_original_profile_dual_stack import once
from pg4260_stable_admission_image import live
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg4152_exact_failed_done_recover import process,durable

SLOT='pg4316-current-failed-dispatch-v1'
ARTIFACT=W/(SLOT+'-artifact')


def constant(raw,name,value):
    nodes=[n for n in ast.parse(raw).body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id==name]
    if len(nodes)!=1:raise ValueError('one named current literal required: '+name)
    return once(raw,ast.get_source_segment(raw,nodes[0]),name+'='+repr(value))


def compiled():
    v=json.loads((W/(role.TOOLS+'-compile')/'manifest.safe.json').read_bytes())
    if v['actualExit']!=0 or v['result']['actualExit']!=0 or v['result']['source']!=role.SOURCE:raise ValueError('actual new-literal compile first')
    return v['result']


def parent_source():
    # Full snapshots also contain configuration/resource fields. Those remain
    # checked separately; the failed-PID1 classifier consumes its exact13 fields.
    fields='Id LoadState ActiveState SubState InvocationID MainPID ControlPID Job Result ExecMainCode ExecMainStatus ExecMainStartTimestampMonotonic ExecMainExitTimestampMonotonic'.split()
    return inspect.getsource(parent)+'\nCURRENT_BINDING='+repr(live())+'\nROOT_FIELDS='+repr(fields)+'''\nfailed_classify=classify
def classify(source,bom,boot,state,rows,done):
    require(type(state)is dict and all(k in state for k in ROOT_FIELDS))
    return failed_classify(source,bom,boot,CURRENT_BINDING,{k:state[k]for k in ROOT_FIELDS},rows,done)
'''


def payload():
    raw=predecessor.archived('pg4144-complete-signed-dispatch-qualification-v1-artifact/dispatch.private.py','5fdbfff67a9aa71aeab60ae897a4e9a23f3038ae7dc6f86dc5f648c201116fe3')
    raw=role.bind_instance(raw)
    for old,new in [('pg4146-complete-signed-owned-recovery-v1',SLOT),('pg4112-canonical-epoch-owned-tools-v1',role.TOOLS),
       ('pg4080-failed-ordinary-full-capture-v1','pg4306-current-failed-authority-read-v1'),
       ('fd1177d10f2713596a32de536a3c71d592563cc3b6decb7194bc6c68ea6c21d8','63269de90bc6bb554e73bde70dcb44bb8e844424c7b364f6597ed1d08aaaf1fd'),
       ('pg4072-failed-parent-pid1-read-v1','pg4302-current-failed-parent-read-v1'),
       ('4b930e614069ccaee34382ba14d84efaf1274dafd262749c5a77d61accb10f38','24e22836fdc96b970a551f2e406e5888d70ea472c930133904cb4a63f9552475'),
       ('128735401165','149622262076'),('130545470134','151432334917'),('all33StartupEntriesPreserved','all37StartupEntriesPreserved'),('SSC287_STOPPED','SSC291_STOPPED')]:raw=raw.replace(old,new)
    fixed=compiled();old=json.loads((W/'pg4112-canonical-epoch-owned-tools-v1-compile/manifest.safe.json').read_bytes())['result']['classHashes']
    nodes=[]
    for n in ast.walk(ast.parse(raw)):
        if isinstance(n,ast.Dict):
            try:value=ast.literal_eval(n)
            except (ValueError,TypeError):continue
            if value==old:nodes.append(n)
    if len(nodes)!=2:raise ValueError('both exact old compiled dictionary pins required')
    segments={ast.get_source_segment(raw,n)for n in nodes}
    for text in segments:raw=raw.replace(text,repr(fixed['classHashes']))
    raw=constant(raw,'JAVA_B64',base64.b64encode(role.java().encode()).decode())
    raw=constant(raw,'INPUT_HASHES',fixed['inputFileHashes'])
    raw=constant(raw,'PARENT_SOURCE',parent_source())
    raw=once(raw,"require(baseline['actors']==EXPECTED_ACTORS)","require(baseline['actors']==EXPECTED_ACTORS)\n require(len(baseline['startup'])==38 and sum(Path(p).suffix=='.exec'for p in baseline['native'])==56)")
    raw=predecessor.inject_declarations(raw)
    # Reuse only the independently qualified general pool boundary function,
    # not the partial controller's Caddy skip, old holders or action entry.
    qualified=predecessor.controller()
    old_check=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='peer_check')
    new_check=next(n for n in ast.parse(qualified).body if isinstance(n,ast.FunctionDef)and n.name=='peer_check')
    raw=once(raw,ast.get_source_segment(raw,old_check),"pool_contract={};exec(POOL_SOURCE,pool_contract)\n"+ast.get_source_segment(qualified,new_check))
    raw='POOL_SOURCE='+repr(inspect.getsource(predecessor.pool))+'\n'+raw
    # Record sanitized stack locations on unknown, without exception text/data.
    raw=once(raw,'import time,sys','import time,sys,traceback')
    raw=once(raw,'except BaseException:\n # If a child/scope ever existed',
      "except BaseException as failure:\n try:durable_save('failure.private.json',encode({'type':type(failure).__name__,'frames':[{'file':Path(t.filename).name,'line':t.lineno,'function':t.name}for t in traceback.extract_tb(failure.__traceback__)]}))\n except OSError:print('FAILURE_CAPTURE_UNAVAILABLE newScopeUnknown=true',flush=True)\n # If a child/scope ever existed")
    if check(raw,'<full current six-unit recovery>'):raise ValueError('whole current recovery static0 required')
    compile(raw,'<current failed cohort six-unit recovery>','exec');return raw


def freeze():
    os.umask(0o077);ARTIFACT.mkdir(mode=0o700);raw=payload().encode();p=ARTIFACT/'dispatch.private.py'
    with p.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    p.chmod(0o400)
    durable(ARTIFACT/'manifest.safe.json',{'payloadSha256':hashlib.sha256(raw).hexdigest(),'source':role.SOURCE,'bytes':len(raw),'operationsIssued':0})
    print(json.dumps({'actualExit':0,'payloadSha256':hashlib.sha256(raw).hexdigest(),'operationsIssued':0}));return 0


def inspect_only():
    raw=(ARTIFACT/'dispatch.private.py').read_bytes();pin=json.loads((ARTIFACT/'manifest.safe.json').read_bytes())
    if raw!=payload().encode()or hashlib.sha256(raw).hexdigest()!=pin['payloadSha256']:raise ValueError('same immutable frozen driver required')
    os.umask(0o077);out=W/(SLOT+'-inspect');out.mkdir(mode=0o700)
    with management_gate(P/'current-management-critical.lock'):
        with(out/'stdout.private.log').open('xb')as stdout,(out/'stderr.private.log').open('xb')as stderr:
            child=subprocess.Popen(SSH+['sudo','-n','python3','-B','-','inspect'],stdin=subprocess.PIPE,stdout=stdout,stderr=stderr)
            durable(out/'start.safe.json',{'owner':process(os.getpid()),'ssh':process(child.pid),'payloadSha256':pin['payloadSha256'],'mode':'inspect','replayAllowed':False})
            child.stdin.write(raw);child.stdin.close();code=child.wait();stdout.flush();stderr.flush();os.fsync(stdout.fileno());os.fsync(stderr.fileno())
    v={'actualExit':code,'source':role.SOURCE,'payloadSha256':pin['payloadSha256'],'mode':'inspect','operationsIssued':0,'formalAccepted':False}
    if code==0:v['result']=json.loads((out/'stdout.private.log').read_bytes())
    durable(out/'manifest.safe.json',v);print(json.dumps(v));return code


if __name__=='__main__':
    if sys.argv[1:]==['freeze']:raise SystemExit(freeze())
    if sys.argv[1:]==['inspect']:raise SystemExit(inspect_only())
    raise SystemExit('freeze or inspect only; recovery not yet exposed')
