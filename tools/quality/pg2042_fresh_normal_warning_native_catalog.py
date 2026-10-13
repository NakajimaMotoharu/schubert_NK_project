"""Current normal-warning Root native ten points; all old26 archives preserved, never imported."""
import datetime
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg1842_warning_inspector_two_point_catalog import catalog_source as previous
from pg2030_fresh_normal_warning_owned_stop_sources import SOURCE,TOOLS

SLOT='pg2042-fresh-normal-warning-native-catalog-v1'


def catalog_source(receipt):
    raw=previous(receipt)
    old="require(completion['genuinePid1Failure']is True and completion['genuinePid1StartDone']is False and completion['endMonotonicUs']==ROOT_END)\nfailed=[r for r in rows if r.get('MESSAGE_ID')=='be02cf6855d2428ba40df7e9d022f03d'and r.get('JOB_ID')=='127250'and r.get('JOB_TYPE')=='start'and r.get('JOB_RESULT')=='failed']\nrequire(len(failed)==1);d=failed[0]"
    new="require(completion['genuinePid1StartDone']is True and completion['normalUnit0or10']is True and completion['completionCode']==10 and completion['endMonotonicUs']==ROOT_END)\ndone_jobs=[r for r in rows if r.get('MESSAGE_ID')=='39f53479d3a045ac8e11786248231fbf'and r.get('JOB_ID')=='187092'and r.get('JOB_TYPE')=='start'and r.get('JOB_RESULT')=='done']\nrequire(len(done_jobs)==1);d=done_jobs[0]"
    if raw.count(old)!=1:raise ValueError('one old failed Root catalog branch required')
    raw=raw.replace(old,new)
    pairs=[('pg1833-native-stop-v1','pg2030-native-stop-v1'),('pg1759-next-day-ordinary-once-v1','pg2015-completed-run-fresh-resume-once-v1'),('oldTwentyArchiveUnchanged','oldTwentySixArchiveUnchanged'),('len(old)==20','len(old)==26'),('9adbf05a-61d0-408b-b51d-ab19c7e5b16a','e31b627c-c0e2-4120-bd64-c0777479e800'),('81404764713','106318294326'),('83018953880','107890801314'),('6c5bf1041fdf45d992dd2b58afd7df09','d6efa3f26d864704b015faa0625da1c0'),('127856','187550'),('128003','187697'),('81623098577','106418451508'),('81634285835','106423392924'),('81635354035','106424517287'),('81635354860','106424518430')]
    for old,new in pairs:
        if old not in raw:raise ValueError('one actual current native catalog binding required: '+old)
        raw=raw.replace(old,new)
    from pyflakes.api import check
    if check('SEALS={}\n'+raw,'<actual current normal Root native catalog>'):raise ValueError('all actual native globals required')
    compile(raw,'<current new normal root native ten points>','exec');return raw


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed native catalog source required')
    post=json.loads((W/'pg2040-fresh-normal-warning-terminal-post-v1/manifest.safe.json').read_bytes())
    if post['actualExit']!=0 or post['productionSource']!=SOURCE or post['allClientAdvisoryFlock0']is not True:raise ValueError('actual current normal full stop post required')
    receipt=(W/TOOLS/'pg2030_parent_receipt.py').read_text();seals={name:post['proofHashes'][name]['sha256']for name in ['before.private.json','after.private.json','complete.private','parent.private.jsonl']}
    raw='SEALS='+repr(seals)+'\n'+catalog_source(receipt);out=W/SLOT;out.mkdir(mode=0o700);(out/'payload.private.py').write_text(raw);started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=60)
    (out/'stderr.private.log').write_bytes(r.stderr);value={'actualExit':r.returncode,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'productionSource':SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
    if not r.returncode:value.update(json.loads(r.stdout))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k not in ['selected','excludedHistorical']}));return r.returncode


if __name__=='__main__':raise SystemExit(main())
