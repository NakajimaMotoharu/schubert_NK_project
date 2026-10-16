"""New before-only applicability: independent encrypted query, history, counts only."""
import types
from pyflakes.api import check
import pg4742_same_day_query_oracle as oracle
import pg4250_current_admission_image as transport
import pg4730_new_current_readonly as current
from pg4434_current_candidate_admission_read import authenticate_host

SLOT='pg4744-same-day-query-preflight-v1'


def payload():
    raw=oracle.source()+r'''
import base64,hashlib,os,stat
from pathlib import Path
require(os.geteuid()==0)
p=Path('/var/lib/pgpt-s1-preservation/pg4728-ssc299-publication-independent-post-v1/after.private.json')
raw=p.read_bytes();require(hashlib.sha256(raw).hexdigest()=='f8dff44c321575ecc5eaa14e76bc9db66bda5850c4d5f81f1d85d4b706a4c601')
require(Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28')
require(hashlib.sha256(Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='f1f6743f8ebe099a8804623f5efef263fa046ca66c46004ade5d469f755fbd80')
path=Path('/etc/schubert-nk/credentials/api-inbox-response-aes-current');s=path.lstat()
require(stat.S_ISREG(s.st_mode)and s.st_uid==s.st_gid==0 and s.st_nlink==1 and stat.S_IMODE(s.st_mode)in {0o400,0o600})
parts=path.read_bytes().split(b'\n');require(path.lstat()==s and len(parts)==4 and parts[:2]==[b'NKKEY1',b'v1']and not parts[-1])
KEY=bytearray(base64.b64decode(parts[2],validate=True));require(len(KEY)==32)
before=json.loads(raw)['rows'];now=datetime.datetime.now(datetime.timezone.utc);projections=[]
try:
 for cutoff in [now,now+datetime.timedelta(hours=2)]:
  expected=candidates(before,cutoff.isoformat());inbox=classify_query_inbox(before,expected['inbox_scan_candidates'],KEY,LAYOUTS)
  day=cutoff.astimezone(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()
  history={step:[r for r in before[BATCH]if r['step']==step and r['business_date']==day]for step in STEPS}
  skips={s for s,rows in history.items()if s not in {'BACKUP_DB','BACKUP_CONFIG'}and any(r['status']=='SUCCESS'for r in rows)}
  require(all(history.values())and {'CLEAN_SESSION','CLEAN_LOG','CLEAN_NOTIFICATION'}<=skips and 'CLEAN_INBOX_OUTBOX'not in skips)
  require(all(not expected[k]for k in ['questions','app_logs','batch_runs','schubert.inbox_inspection_progress','schubert.log_cleanup_progress','web_receipt_references']))
  require(all(max(r['attempt']for r in rows)<99 for rows in history.values()))
  projections.append({'cutoff':cutoff.isoformat(),'businessDate':day,'independentApplicability':True,'skippedSteps':sorted(skips),'inboxDeleted':len(inbox['deleted']),'inboxProtected':len(inbox['protected']),'retainedNotificationCandidates':len(expected['notifications']),'outboxDeletes':len(expected[OUTBOX])+len(expected['schubert.mq_outbox'])})
finally:KEY[:]=b'\0'*len(KEY)
require(p.read_bytes()==raw)
print(json.dumps({'actualExit':0,'beforeSha256':hashlib.sha256(raw).hexdigest(),'projections':projections,'rawExported':False,'plaintextLogged':False,'dbOrClockChanged':False,'rootStartIssued':False,'formalAccepted':False}))
'''
    if check(raw,'<independent query preflight>'):raise ValueError('complete emitted namespace')
    compile(raw,'<before-only encrypted query preflight>','exec');return raw


def main():
    authenticate_host()
    execute=types.FunctionType(transport.execute.__code__,{**vars(transport),'SOURCE':current.SOURCE})
    return execute(SLOT,payload(),45)


if __name__=='__main__':raise SystemExit(main())
