"""Independent SS331/341 same-day newrun: every Backup, successful cleanup skip, protected Inbox."""
import ast
import datetime
import inspect
from pg1196_completed_rows_oracle import require,instant,BATCH,LOG,SESSION,OUTBOX,STEPS
import pg1196_completed_rows_oracle as http
from pg1769_next_day_rows_oracle import delta,http_validation_source,validate_http
from pg478_cleanup_oracle import candidates
import pg478_cleanup_oracle as selectors
from pg1766_next_day_independent_candidates import classify_inbox


def qualify(before,now,run,cutoff,upper):
    require(type(before)is dict and type(now)is dict and set(before)==set(now)and len(before)==24)
    start,end=instant(cutoff),instant(upper);require(start<end)
    day=start.astimezone(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()
    expected=candidates(before,cutoff);inbox=classify_inbox(before,expected['inbox_scan_candidates'])
    history={step:[r for r in before[BATCH]if r['step']==step and r['business_date']==day]for step in STEPS}
    require(all(history.values()))
    skips={step for step,rows in history.items()if step not in {'BACKUP_DB','BACKUP_CONFIG'}and any(r['status']=='SUCCESS'for r in rows)}
    # This limited independent route admits protected missing AUTH_SESSION only.
    # Other cleanup candidates require a separate oracle, never assumed deletable.
    require('CLEAN_INBOX_OUTBOX'not in skips and not inbox['deleted'])
    require(all(not expected[k]for k in ['notifications','questions','app_logs','batch_runs','schubert.inbox_inspection_progress','schubert.log_cleanup_progress','web_receipt_references']))
    expected_deleted={OUTBOX:expected[OUTBOX],'schubert.mq_outbox':expected['schubert.mq_outbox']}
    require('CLEAN_SESSION'in skips and 'CLEAN_LOG'in skips)
    added={}
    for table,rows in before.items():
        key='run_id'if table in {'schubert.inbox_inspection_progress','schubert.log_cleanup_progress'}else'client_address'if table=='schubert.login_ip_attempts'else'receipt_id'if table=='schubert_web_session.web_receipt_references'else'message_id'if table=='schubert.request_inbox'else'id'
        added[table]=delta(rows,now[table],key,expected_deleted.get(table,[]))
    require(all(not rows for table,rows in added.items()if table not in {BATCH,LOG,SESSION,OUTBOX,'schubert.inbox_inspection_progress'}))
    batch=added[BATCH];require(len(batch)==10 and {r['step']for r in batch}==STEPS)
    maximum=max(r['id']for r in before[BATCH]);ids=set()
    for row in batch:
        require(row['run_id']==run and row['business_date']==day and type(row['id'])is int and row['id']>maximum and row['id']not in ids);ids.add(row['id'])
        require(type(row['attempt'])is int and row['attempt']==max(r['attempt']for r in history[row['step']])+1)
        require(start<=instant(row['started_at'])<=instant(row['ended_at'])<=end)
        require(all(type(row[k])is int for k in ['target_count','success_count','failure_count','byte_count'])and row['failure_count']==0)
        if row['step']in {'BACKUP_DB','BACKUP_CONFIG'}:
            count=1 if row['step']=='BACKUP_DB'else 2
            require(row['status']=='SUCCESS'and row['target_count']==row['success_count']==count and row['byte_count']>0 and row['error_code']is row['error_summary']is None)
        elif row['step']in skips:
            require(row['status']=='SKIPPED'and row['error_code']=='ALREADY_SUCCESSFUL'and row['error_summary']=='step already successful for business date')
            require(row['started_at']==row['ended_at']and row['target_count']==row['success_count']==row['byte_count']==0)
        else:
            require(row['step']=='CLEAN_INBOX_OUTBOX'and row['status']=='WARNING'and row['error_code']=='PROTECTED_RECORDS'and row['error_summary']=='protected records retained')
            outboxes=sum(len(expected_deleted[t])for t in expected_deleted)
            require(row['target_count']==outboxes+len(inbox['protected'])and row['success_count']==outboxes and row['byte_count']==0)
    progress=added['schubert.inbox_inspection_progress'];require(len(progress)==1);p=progress[0]
    require(p['run_id']==run and instant(p['cutoff'])==start and start<=instant(p['completed_at'])<=end)
    require(p['inspected_count']==p['protected_count']==len(inbox['protected'])and p['deleted_count']==0 and p['after_message_id']==max(inbox['protected'],default=None))
    result=validate_http(added,start,end)
    return {**result,'independentRowsQualified':True,'distinctLogicalNewRun':True,'newBackupSteps':2,'newSkippedSteps':len(skips),'newProtectedWarningSteps':1,'expectedInboxProtected':len(inbox['protected']),'expectedOutboxDeleted':sum(map(len,expected_deleted.values())),'wholeAccepted':False}


def source():
    raw=inspect.getsource(http)
    nodes=[n for n in ast.parse(raw).body if isinstance(n,(ast.Import,ast.ImportFrom,ast.Assign))or isinstance(n,ast.FunctionDef)and n.name in {'require','instant','identifier','ciphertext','key_version'}]
    selector_source='\n'.join(inspect.getsource(f)for f in [selectors.instant,selectors.older,selectors.candidates])
    result='\n'.join(ast.get_source_segment(raw,n)for n in nodes)+'\n'+http_validation_source()+inspect.getsource(delta)+'\n'
    result+="_selectors={'datetime':datetime,'UTC':datetime.timezone.utc};exec("+repr(selector_source)+",_selectors)\ncandidates=_selectors['candidates']\n"
    result+=inspect.getsource(classify_inbox)+'\n'+inspect.getsource(qualify)
    return result
