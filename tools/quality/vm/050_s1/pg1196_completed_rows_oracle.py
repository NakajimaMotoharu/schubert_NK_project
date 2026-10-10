"""Independent DDL/SS341/312/351 completed-resume and anonymous HTTP deltas.

Data only; no Production method, database connection, expected generation or
operation authority. BUG1053/YKT822; PT-DEP-1196001..004.
"""
import datetime
import json
import re
import uuid

LIMIT = 64*1024*1024
BATCH='schubert.batch_runs';LOG='schubert.app_logs'
SESSION='schubert_web_session.web_http_sessions';OUTBOX='schubert_web_session.web_log_outbox'
STEPS={'BACKUP_DB','BACKUP_CONFIG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER','CLEAN_EXPIRY'}


def require(ok):
    if not ok:raise ValueError('completed data postcondition refused')


def output_bound(code,size):
    require(type(code)is int and code==0 and type(size)is int and 0<size<=LIMIT)


def instant(value):
    require(type(value)is str);v=datetime.datetime.fromisoformat(value.replace('Z','+00:00'));require(v.tzinfo is not None);return v


def identifier(value):
    require(type(value)is str);v=uuid.UUID(value);require(str(v)==value and v.version==4)


def ciphertext(value):
    require(type(value)is str and value.startswith('\\x')and re.fullmatch('[0-9a-f]+',value[2:])is not None and len(value[2:])%2==0 and len(value[2:])//2>28)


def key_version(value):
    require(type(value)is str and re.fullmatch('[A-Za-z0-9][A-Za-z0-9._-]{0,15}',value)is not None)


def after(old,new,run,lower,upper):
    require(type(old)is dict and type(new)is dict and set(old)==set(new)and len(old)==24)
    identifier(run);start,end=instant(lower),instant(upper);require(start<=end)
    added={}
    for table,before in old.items():
        now=new[table];require(type(before)is list and type(now)is list and all(type(r)is dict for r in [*before,*now]))
        seals=lambda rows:[json.dumps(r,sort_keys=True,separators=(',',':'))for r in rows]
        a,b=seals(before),seals(now);require(len(set(a))==len(a)and len(set(b))==len(b)and set(a)<=set(b))
        added[table]=[r for r,s in zip(now,b)if s not in set(a)]
        if table not in {BATCH,LOG,SESSION,OUTBOX}:require(not added[table])
    require({BATCH,LOG,SESSION,OUTBOX}<=set(old))
    batch=added[BATCH];require(len(batch)==10 and {r.get('step')for r in batch}==STEPS)
    for row in batch:
        require(row['run_id']==run and row['business_date']=='2026-10-10'and row['status']=='SKIPPED'and row['error_code']=='ALREADY_SUCCESSFUL'and row['error_summary']=='step already successful for business date')
        require(all(type(row[k])is int and row[k]==0 for k in ['target_count','success_count','failure_count','byte_count']))
        require(start<=instant(row['started_at'])==instant(row['ended_at'])<=end)
    logs,events,sessions=added[LOG],added[OUTBOX],added[SESSION]
    require(logs and sessions and len(logs)==len(events))
    event_ids=set()
    for row in events:
        identifier(row['message_id']);identifier(row['correlation_id']);require(row['message_id']not in event_ids);event_ids.add(row['message_id'])
        require(row['layout_id']=='WLGEVT01'and row['layout_version']=='001'and row['status']=='SENT'and row['last_error_code']is None and row['lease_owner']is None and row['lease_until']is None)
        require(type(row['attempt_count'])is int and 0<=row['attempt_count']<=100 and start<=instant(row['created_at'])<=instant(row['sent_at'])<=end)
        ciphertext(row['payload_ciphertext']);key_version(row['key_version'])
    source_ids=set()
    for row in logs:
        identifier(row['source_message_id']);require(row['source_message_id']not in source_ids);source_ids.add(row['source_message_id'])
        require(row['message_id']==row['source_message_id']==row['correlation_id'])
        require((row['service'],row['category'],row['level'],row['action'],row['http_method'],row['status_code'])==('WEB','REQUEST','INFO','HTTP_REQUEST_COMPLETED','GET',200))
        require(row['request_uri']in {'/login','/css/**'}and row['actor_user_id']is None and row['actor_username']is None and row['security_hold_until']is None)
        require(start<=instant(row['logged_at'])<=end and type(row['message'])is str and 1<=len(row['message'].encode())<=512)
        require(type(row['details'])is dict and len(json.dumps(row['details'],ensure_ascii=False).encode())<=1024)
        require(type(row['duration_ms'])is int and 0<=row['duration_ms']<=999999999)
    require(source_ids==event_ids)
    for row in sessions:
        identifier(row['id']);key_version(row['key_version']);ciphertext(row['attributes_ciphertext'])
        require(type(row['session_id_hash'])is str and re.fullmatch('[0-9a-f]{64}',row['session_id_hash'])is not None)
        require(type(row['max_inactive_seconds'])is int and 1<=row['max_inactive_seconds']<=28800 and type(row['version'])is int and 0<=row['version']<=999999999)
        require(start<=instant(row['created_at'])<=instant(row['last_accessed_at'])<=end and instant(row['last_accessed_at'])<=instant(row['expires_at']))
    return {'tables':24,'oldRowsRetained':True,'newSkippedSteps':10,'newAnonymousHttpLogs':len(logs),'newAnonymousSessions':len(sessions),'newSentOutbox':len(events),'logOutboxOneToOne':True,'rawIdsExported':False,'wholeAccepted':False}
