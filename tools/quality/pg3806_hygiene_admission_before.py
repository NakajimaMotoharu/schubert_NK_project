"""Authenticate immutable pre-start image and same-day eligibility, never live DB mutation."""
import inspect
import json
import pg2698_operation_admission_before as previous
from pg3798_hygiene_current_observer import SOURCE
from pg3802_hygiene_current_noargs_once import SLOT as ONCE
from pg3804_hygiene_current_live_binding import SLOT as LIVE
from pg1446_current_cold_stage import W

SLOT='pg3806-hygiene-admission-before-v1'
AFTER='4eb5ac214713b201394035938cb931796f8ec3e0a81885e319ee2993500def76'


def payload():
    live=json.loads((W/LIVE/'manifest.safe.json').read_bytes())
    if live.get('actualExit')!=0 or live.get('productionSource')!=SOURCE:raise ValueError('genuine same-source new Root required')
    raw=previous.BODY.replace('pg2684-operation-current-noargs-once-v2',ONCE)
    marker="require(len(v['native'])==41 and sum(pathlib.Path(k).suffix=='.exec'for k in v['native'])==28)"
    if raw.count(marker)!=1:raise ValueError('one exact original native schema boundary')
    extra="post=pathlib.Path('/var/lib/pgpt-s1-preservation/pg3794-hygiene-publication-independent-post-v1/after.private.json').read_bytes()\nrequire(hashlib.sha256(post).hexdigest()=="+repr(AFTER)+" and raw==post and v==json.loads(post))\nrequire(sum(pathlib.Path(k).suffix=='.exec'for k in v['native'])==34)\n"
    raw=raw.replace(marker,extra)
    raw=raw[:raw.index("print(json.dumps({'actualExit':0,")]
    raw+='''
import datetime
cut=datetime.datetime.fromisoformat(CUT.replace('Z','+00:00'));day=cut.astimezone(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()
steps={'BACKUP_DB','BACKUP_CONFIG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER','CLEAN_EXPIRY'}
history={step:[r for r in v['rows']['schubert.batch_runs']if r['step']==step and r['business_date']==day]for step in steps}
require(all(history.values()))
print(json.dumps({'actualExit':0,'privateBeforeSha256':hashlib.sha256(raw).hexdigest(),'nativeEntries':len(v['native']),'execEntries':34,'businessDate':day,'sameDayHistoryCount':sum(map(len,history.values())),'historyStepCount':len(history),'rawExported':False,'productionCalls':0,'liveDbRowsRead':0}))
'''
    return 'CUT='+repr(live['binding']['cutoff'])+'\n'+raw


def before():
    value=json.loads((W/SLOT/'manifest.safe.json').read_bytes())
    if value.get('actualExit')!=0 or value.get('productionSource')!=SOURCE or value['guest'].get('privateBeforeSha256')!=AFTER:raise ValueError('actual immutable same-source before qualification required')
    return AFTER


def main():
    raw=inspect.getsource(previous.main).replace('pg2684-operation-current-noargs-once-v2',ONCE).replace('pg2686-operation-current-live-binding-v1',LIVE)
    values={**previous.__dict__,'SLOT':SLOT,'BODY':payload(),'production':lambda:SOURCE}
    exec(compile(raw,'<new immutable admission-image qualification>','exec'),values);return values['main']()


if __name__=='__main__':raise SystemExit(main())
