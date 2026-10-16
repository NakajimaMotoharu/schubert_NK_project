"""Independent before-only applicability of SS341 same-day oracle, no Root or DB writes."""
import types
from pyflakes.api import check
import pg2078_current_same_day_rows_oracle as oracle
import pg4730_new_current_readonly as current
import pg4250_current_admission_image as transport
from pg4434_current_candidate_admission_read import authenticate_host

SLOT='pg4732-same-day-oracle-preflight-v1'


def payload():
    raw=oracle.source()+r'''
import hashlib
from pathlib import Path
p=Path('/var/lib/pgpt-s1-preservation/pg4728-ssc299-publication-independent-post-v1/after.private.json')
raw=p.read_bytes();require(hashlib.sha256(raw).hexdigest()=='f8dff44c321575ecc5eaa14e76bc9db66bda5850c4d5f81f1d85d4b706a4c601')
require(Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28')
require(hashlib.sha256(Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='f1f6743f8ebe099a8804623f5efef263fa046ca66c46004ade5d469f755fbd80')
before=json.loads(raw)['rows'];now=datetime.datetime.now(datetime.timezone.utc)
projections=[]
for cutoff in [now,now+datetime.timedelta(hours=2)]:
 day=cutoff.astimezone(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()
 expected=candidates(before,cutoff.isoformat());inbox=classify_inbox(before,expected['inbox_scan_candidates'])
 history={step:[r for r in before[BATCH]if r['step']==step and r['business_date']==day]for step in STEPS}
 skips={s for s,rows in history.items()if s not in {'BACKUP_DB','BACKUP_CONFIG'}and any(r['status']=='SUCCESS'for r in rows)}
 missing=[s for s,rows in history.items()if not rows]
 other={k:len(expected[k])for k in ['notifications','questions','app_logs','batch_runs','schubert.inbox_inspection_progress','schubert.log_cleanup_progress','web_receipt_references']}
 compatible=not missing and 'CLEAN_INBOX_OUTBOX'not in skips and not inbox['deleted']and not any(other.values())and {'CLEAN_SESSION','CLEAN_LOG'}<=skips
 projections.append({'cutoff':cutoff.isoformat(),'businessDate':day,'sameDayOracleCompatible':compatible,'history':{s:sorted(set(r['status']for r in rows))for s,rows in history.items()},'maxAttempts':{s:max([r['attempt']for r in rows],default=0)for s,rows in history.items()},'skippedSteps':sorted(skips),'unhandledCandidateCounts':other,'inboxProtected':len(inbox['protected']),'inboxDeleted':len(inbox['deleted']),'outboxDeletes':len(expected[OUTBOX]),'mqOutboxDeletes':len(expected['schubert.mq_outbox'])})
print(json.dumps({'actualExit':0,'beforeSha256':hashlib.sha256(raw).hexdigest(),'projections':projections,'dbOrClockChanged':False,'rootStartIssued':False,'formalAccepted':False}))
'''
    if check(raw,'<independent same-day before preflight>'):raise ValueError('all independent globals required')
    compile(raw,'<before-only SS341 applicability>','exec');return raw


def main():
    authenticate_host()
    execute=types.FunctionType(transport.execute.__code__,{**vars(transport),'SOURCE':current.SOURCE})
    return execute(SLOT,payload(),45)


if __name__=='__main__':raise SystemExit(main())
