"""Derive independent cutoff candidates and safe delta shapes from saved images, no DB read."""
import inspect
import pg478_cleanup_oracle as selectors
import pg4584_current_admission_image as admission
from pg1446_current_cold_stage import W
import json

SLOT='pg4630-current-day-candidate-summary-v1'


def payload():
    return 'SOURCE='+repr(admission.SOURCE)+'\nBOM='+repr(admission.BOM)+'\nBINDING='+repr(admission.live())+'\n'+r'''
import collections,datetime,hashlib,json,os,pathlib
UTC=datetime.timezone.utc
require=lambda v:None if v else(_ for _ in()).throw(ValueError('saved image summary refused'))
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28')
base=pathlib.Path('/var/lib/pgpt-s1-preservation/pg4628-current-raw24-capture-v1')
br=(base/'before.private.json').read_bytes();ar=(base/'after.private.json').read_bytes()
require(hashlib.sha256(br).hexdigest()=='21c86465bd24d2a8358472b0dc1cfcaee93c80bb8b113295da577c4e981385fe'and hashlib.sha256(ar).hexdigest()=='d6d3a6fe639feb3e898d18b7c5ac6281efe8ef5d4767a7eaf597f3254bbc52f3')
before=json.loads(br)['database']['rows'];after=json.loads(ar)['rows']
'''+'\n'.join(inspect.getsource(fn)for fn in [selectors.instant,selectors.older,selectors.candidates])+r'''
expected=candidates(before,BINDING['cutoff']);day=instant(BINDING['cutoff']).astimezone(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()
history=collections.Counter((r['step'],r['status'])for r in before['schubert.batch_runs']if r['business_date']==day)
actual_steps=[{k:r[k]for k in ['step','status','attempt','target_count','success_count','failure_count','byte_count','error_code']}for r in after['schubert.batch_runs']if r['run_id']==BINDING['run']]
deltas={};newlogs=[]
for table in before:
 key='run_id'if table.endswith(('inbox_inspection_progress','log_cleanup_progress'))else'client_address'if table.endswith('login_ip_attempts')else'receipt_id'if table.endswith('web_receipt_references')else'message_id'if table.endswith('request_inbox')else'id'
 a={str(r[key]):r for r in before[table]};b={str(r[key]):r for r in after[table]}
 changed=collections.Counter(tuple(sorted(k for k in a[i]if a[i][k]!=b[i].get(k)))for i in a.keys()&b.keys()if a[i]!=b[i])
 deltas[table]={'added':len(b.keys()-a.keys()),'removed':len(a.keys()-b.keys()),'changed':sum(changed.values()),'changedFieldCounts':[[list(k),v]for k,v in changed.items()]}
 if table=='schubert.app_logs':newlogs=[b[i]for i in b.keys()-a.keys()]
logtypes=collections.Counter(tuple(str(r.get(k))for k in ['service','category','level','action','http_method','status_code'])for r in newlogs)
routes=collections.Counter(r.get('request_uri')if r.get('request_uri')in ['/login','/actuator/health/readiness','/actuator/info']else'OTHER'for r in newlogs)
outboxes={r['message_id']:r for r in before['schubert_web_session.web_log_outbox']}
linked=collections.Counter(('before-outbox:'+outboxes[r['source_message_id']]['status'])if r.get('source_message_id')in outboxes else'not-before-web-outbox'for r in newlogs)
manifest=pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(manifest).hexdigest()==BOM and json.loads(manifest)['source']['commit']==SOURCE)
print(json.dumps({'actualExit':0,'source':SOURCE,'businessDay':day,'beforeDayHistory':[[list(k),v]for k,v in history.items()],'expectedCandidateCounts':{k:len(v)for k,v in expected.items()},'actualSteps':actual_steps,'deltas':deltas,'newLogTypes':[[list(k),v]for k,v in logtypes.items()],'newLogRoutes':dict(routes),'newLogsLinkedToBeforeWebOutbox':dict(linked),'rawExported':False,'oracleNotYetQualified':True,'startsStopsDbReadsWrites':0,'formalAccepted':False}))
'''


def main():
    v=json.loads((W/'pg4628-current-raw24-capture-v1/manifest.safe.json').read_bytes())
    if v['actualExit']!=0 or v['source']!=admission.SOURCE:raise ValueError('saved fresh full24 capture0 first')
    return admission.execute(SLOT,payload())


if __name__=='__main__':raise SystemExit(main())
