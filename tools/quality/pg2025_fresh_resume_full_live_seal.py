"""Whole current new-activation seal with genuine normal terminal, independent rows and owned identities."""
import ast
import datetime
import hashlib
import inspect
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg1702_new_source_completed_seal import payload as previous,once
from pg2021_fresh_resume_terminal_receipt import classify,GUEST
from pg2023_fresh_resume_rows_oracle import oracle_source
from pg2015_completed_run_fresh_resume_once import SOURCE,BOM,RUN

SLOT='pg2025-fresh-resume-full-live-seal-v1'


def constant(raw,name,value):
    nodes=[n for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id==name for t in n.targets)]
    if len(nodes)!=1:raise ValueError('one '+name+' constant required')
    return once(raw,ast.get_source_segment(raw,nodes[0]),name+'='+repr(value))


def payload(binding):
    raw=previous()
    marker="out=pathlib.Path('/var/lib/pgpt-s1-preservation/pg2021-fresh-resume-terminal-receipt-v1')"
    guard='BINDING='+repr(binding)+'\n'+inspect.getsource(classify)+'\n'+GUEST[:GUEST.index(marker)]
    raw=constant(raw,'GUARD',guard)
    model=oracle_source().replace('def qualify(old,new,run,cutoff,lower,upper):','def qualify_resume(old,new,run,cutoff,lower,upper):')
    model+="\ndef qualify(old,new,cutoff,done,upper):\n    require(instant(cutoff)<=instant(done)<=instant(upper))\n    return qualify_resume(old,new,'"+RUN+"',cutoff,'2026-10-13T01:15:32.188849+00:00',upper)\n"
    raw=constant(raw,'ORACLE',model)
    changes=[('pg1702-new-source-completed-seal-v1',SLOT),('pg1699-new-current-ordinary-once-v1/before.private.json','pg2015-completed-run-fresh-resume-once-v1/before.private.json'),('ef9ddffcf813c6e4f4b8bb6379c30e5e0d87503a4abaf46859976a32fa8bfecb','fd6412f31de9af59219a0fe28f49ce0d073b074a7ff83ca3516a22e462568b83'),('2741c4546afad6c1e8b6efbd53dfb58144edf7bb',SOURCE),('195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1',BOM),('PG1638','PG1846'),('pg1638-manifest.sig','pg1846-manifest.sig'),('02e941b9-1c52-4018-a193-63dd00b269af',RUN),('2026-10-12T14:19:28.968927Z','2026-10-12T18:20:32.598894Z'),('40da389f-23fc-4ad4-a71b-cf72a6bd5a62','e31b627c-c0e2-4120-bd64-c0777479e800')]
    for old,new in changes:
        if old not in raw:raise ValueError('actual current binding missing '+old)
        raw=raw.replace(old,new)
    from pyflakes.api import check
    if check(raw,'<actual whole current normal resume seal>'):raise ValueError('all full seal globals required')
    compile(raw,'<same current new activation full independent live seal>','exec');return raw


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed full seal tools required')
    term=json.loads((W/'pg2021-fresh-resume-terminal-receipt-v1/manifest.safe.json').read_bytes());rows=json.loads((W/'pg2023-fresh-resume-rows-oracle-v1/manifest.safe.json').read_bytes());live=json.loads((W/'pg2019-fresh-resume-live-binding-complete-v1/manifest.safe.json').read_bytes())
    if any(v['actualExit']!=0 for v in [term,rows,live])or term['productionSource']!=SOURCE or rows['independentRowsQualified']is not True:raise ValueError('current actual terminal/independent rows/live binding required')
    raw=payload(live['binding']);out=W/SLOT;out.mkdir(mode=0o700);(out/'payload.private.py').write_text(raw);started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=120)
    (out/'stderr.private.log').write_bytes(r.stderr);value={'actualExit':r.returncode,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'productionSource':SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
    if not r.returncode:value.update(json.loads(r.stdout))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
