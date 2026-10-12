"""Root13 native catalog: failed PID1 remains failed; old twenty never imported."""
import ast
import datetime
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg1708_new_source_native_catalog import catalog_source as old_catalog
from pg1833_readonly_parent_state_sources import SOURCE,TOOLS

SLOT='pg1839-warning-current-native-catalog-v1'
ROOT_START=81404764713
ROOT_END=83018953880


def catalog_source(receipt):
    raw=old_catalog()
    bindings={'pg1703-native-stop-v1':'pg1833-native-stop-v1',
              'pg1699-new-current-ordinary-once-v1':'pg1759-next-day-ordinary-once-v1',
              'oldFourteenArchiveUnchanged':'oldTwentyArchiveUnchanged'}
    for old,new in bindings.items():
        if old not in raw:raise ValueError('one fixed catalog binding required')
        raw=raw.replace(old,new)
    raw=raw.replace('66941284515',str(ROOT_START)).replace('68542820690',str(ROOT_END)).replace('len(old)==14','len(old)==20')
    top_done=[n for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='done'for t in n.targets)]
    if len(top_done)!=1:raise ValueError('one top-level parent receipt boundary required')
    first=sum(len(line)for line in raw.splitlines(keepends=True)[:top_done[0].lineno-1]);last=raw.index('offset=',first)
    raw=raw[:first]+'''original=pathlib.Path('/var/lib/schubert-nk/maintenance/attempts/9adbf05a-61d0-408b-b51d-ab19c7e5b16a.done').read_bytes()
completion=completed(rows,original)
require(completion['genuinePid1Failure']is True and completion['genuinePid1StartDone']is False and completion['endMonotonicUs']==ROOT_END)
failed=[r for r in rows if r.get('MESSAGE_ID')=='be02cf6855d2428ba40df7e9d022f03d'and r.get('JOB_ID')=='127250'and r.get('JOB_TYPE')=='start'and r.get('JOB_RESULT')=='failed']
require(len(failed)==1);d=failed[0]
'''+raw[last:]
    old="for role,unit,inv in [('api','schubert-nk-api.service','e884f0ed2ac649a5853b20d281600b67'),('web','schubert-nk-web.service','fb2ccde2df8b455280c7e8ce489b3365')]:"
    if raw.count(old)!=1:raise ValueError('one actual ordinary generation binding required')
    raw=raw.replace(old,"for role,unit in [('api','schubert-nk-api.service'),('web','schubert-nk-web.service')]:\n inv=before['units'][unit]['InvocationID'];require(type(inv)is str and re.fullmatch('[a-f0-9]{32}',inv)is not None)")
    raw=receipt+'\n'+raw
    compile(raw,'<actual Root13 failed manager eight native>','exec')
    return raw


def main():
    os.umask(0o077)
    post=json.loads((W/'pg1838-warning-terminal-independent-post-v1/manifest.safe.json').read_bytes())
    if post['actualExit']!=0 or post['productionSource']!=SOURCE or post['allClientAdvisoryFlock0']is not True:raise ValueError('separate actual normal stop post required')
    receipt=(W/TOOLS/'pg1833_parent_receipt.py').read_text()
    seals={name:post['proofHashes'][name]['sha256']for name in ['before.private.json','after.private.json','complete.private','parent.private.jsonl']}
    raw='SEALS='+repr(seals)+'\n'+catalog_source(receipt)
    out=W/SLOT;out.mkdir(mode=0o700);(out/'payload.private.py').write_text(raw)
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=60)
    (out/'stderr.private.log').write_bytes(r.stderr)
    result={'actualExit':r.returncode,'productionSource':SOURCE,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
    if not r.returncode:result.update(json.loads(r.stdout))
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True)
    print(json.dumps({k:v for k,v in result.items()if k not in ['selected','excludedHistorical']}));return r.returncode


if __name__=='__main__':raise SystemExit(main())
