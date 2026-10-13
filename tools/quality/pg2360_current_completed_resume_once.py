"""One explicit fresh activation of current completed run, not lost-response replay."""
import ast
import datetime
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg2358_current_completed_resume_observer import namespace
from pg2338_current_reloaded_pair_proof import body as whole,SOURCE
from pg2015_completed_run_fresh_resume_once import body as template
from pg2304_current_completed_resume_sources import BOM,RUN

SLOT='pg2360-current-completed-resume-once-v1'
BEFORE='6873c5eb138bbd3dbd6a8e00398738b837dca149325db0ff555d0901bd1b10ec'
NATIVE='9bf72ad074cbe798ef6082d31f25be89fe7cf3e3d31be484a997ce4b0b82c955'


def body():
    raw=template()
    for a,b in [('pg2010','pg2358'),('pg2015-completed-run-fresh-resume-once-v1',SLOT),('0fd734195b4d5338f6b7e860e087cce561d49562',SOURCE),('ee75d0cd61457462eca59e67f5af2d8e677427071514940f3fb594ba93a026d7',BOM),('PG1846','PG2126'),('4148e3e8-f107-431a-ab27-d6e6d1f1772e',RUN),('fd6412f31de9af59219a0fe28f49ce0d073b074a7ff83ca3516a22e462568b83',BEFORE),('b9dce89b8ab71f077937a4eb2fd87141d5e7e3dcf300e3614080d42fd51a2683',NATIVE),('require(len(records)==26)','require(len(records)==10)')]:raw=raw.replace(a,b)
    raw=raw.replace("declaration=exec_record(after['configuration']", "accepted_before={**after,'configuration':dict(current_view)}\ndeclaration=exec_record(accepted_before['configuration']")
    raw=raw.replace('json.dumps(after,sort_keys=True)','json.dumps(accepted_before,sort_keys=True)')
    raw=raw.replace("persist('before.private.json',after)","persist('before.private.json',accepted_before)")
    return raw


def payload(hashes):
    raw=whole().replace('PEER_CLOSED=False','PEER_CLOSED=True')
    tree=ast.parse(raw);scope=next(n for n in tree.body if isinstance(n,ast.Try)and any(isinstance(x,ast.FunctionDef)and x.name=='snapshot'for x in n.body))
    lines=raw.splitlines(keepends=True);end=next(i for i in range(scope.lineno-1,scope.end_lineno)if lines[i].startswith('finally:'))
    return_value='\nprint(json.dumps(current))\nraise SystemExit(r.returncode)\n'
    out='WATCH_FILES='+repr(hashes)+'\n'+''.join(lines[:end])+'\n'.join('    '+line if line else line for line in body().splitlines())+'\n'+''.join(lines[end:scope.end_lineno])+return_value
    if check(out,'<current whole completed resume once>'):raise ValueError('all actual once globals required')
    compile(out,'<actual current completed resume once>','exec');return out


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed operator required')
    post=json.loads((W/'pg2356-current-runtime-verification-post-v1/manifest.safe.json').read_bytes())
    if not(post['actualExit']==0 and post['productionSource']==SOURCE and post['guest']['verificationOnlyNormalScopeConfirmed'] and post['guest']['allClientAdvisoryFlock0']):raise ValueError('actual qualified normal verification post required')
    if not(W/'pg2358-watch-v1.started').exists()or(W/'pg2358-watch-v1.exit').exists():raise ValueError('new live observer required')
    frames=[json.loads(x)for x in(W/'pg2358-parent-watch-v1.private.jsonl').read_bytes().splitlines()]
    states=[x['states']for x in frames if 'states'in x]
    if not states or any(v['MainPID']!='0'or v['ControlPID']!='0'or v['Job']for v in states[-1].values()):raise ValueError('new observer initial quiescence required')
    hashes={n:hashlib.sha256(s.encode()).hexdigest()for n,s in namespace()['files']().items()}
    if {p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in(P/'pg2358-observer-stage-v1').iterdir()}!=hashes:raise ValueError('fixed full observer closure required')
    out=W/SLOT;out.mkdir(mode=0o700);raw=payload(hashes);(out/'payload.private.py').write_text(raw)
    operator=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(r.stderr);(out/'stdout.private.json').write_bytes(r.stdout)
    v={'actualExit':r.returncode,'operatorSource':operator,'sourceQualified':operator==subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()and not subprocess.check_output(['git','status','--porcelain']),'productionSource':SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':start,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False,'clientSuccessIsNotParentSuccess':True,'replayForbidden':True}
    if not r.returncode:v['guest']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(v,sort_keys=True));print(json.dumps(v));return r.returncode


if __name__=='__main__':raise SystemExit(main())
