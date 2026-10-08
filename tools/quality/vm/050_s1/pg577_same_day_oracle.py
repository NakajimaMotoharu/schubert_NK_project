"""SS331 §8.3/SSC200 independent full-row same-day skip projection, not test skips."""
import datetime

STEPS=('BACKUP_DB','BACKUP_CONFIG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER','CLEAN_EXPIRY')
COLUMNS=set('attempt business_date byte_count ended_at error_code error_summary expiry_after_count expiry_before_count expiry_cutoff_at failure_count id run_id started_at status step success_count target_count'.split())
OLD_RUN='b7e73994-b951-4696-bdd1-cfbc8a10e734'
RUN='b62b6984-ffc2-4c9d-aea9-e232d9d1ec9e'


def require(value):
    if not value:raise ValueError('independent same-day step oracle refused')


def instant(value):
    require(type(value)is str)
    t=datetime.datetime.fromisoformat(value.replace('Z','+00:00'));require(t.tzinfo is not None);return t


def verify(before,after,cutoff):
    require(type(before)is list and type(after)is list and len(before)==472 and len(after)==482)
    require(all(type(r)is dict and type(r.get('id'))is int and r['id']>0 for r in before+after))
    old={r['id']:r for r in before};current={r['id']:r for r in after}
    require(len(old)==472 and len(current)==482 and all(current.get(k)==v for k,v in old.items()))
    added=[r for k,r in current.items()if k not in old];require({r['step']for r in added}==set(STEPS))
    rows={r['step']:r for r in added};require(len(rows)==10)
    boundary=instant(cutoff)
    for step,r in rows.items():
        require(set(r)==COLUMNS and r['run_id']==RUN and r['business_date']=='2026-10-08')
        require(type(r['attempt'])is int and 1<=r['attempt']<=99)
        prior=[v for v in before if v['business_date']==r['business_date']and v['step']==step]
        require(prior and r['attempt']==max(v['attempt']for v in prior)+1)
        require(boundary<=instant(r['started_at'])<=instant(r['ended_at']))
        require(all(type(r[k])is int and r[k]>=0 for k in ('target_count','success_count','failure_count','byte_count')))
        require(all(r[k]is None for k in ('expiry_cutoff_at','expiry_before_count','expiry_after_count')))
        if step in ('BACKUP_DB','BACKUP_CONFIG'):
            count=1 if step=='BACKUP_DB'else 2
            require(r['status']=='SUCCESS'and(r['target_count'],r['success_count'],r['failure_count'])==(count,count,0)and r['byte_count']>0)
            require(r['error_code']is None and r['error_summary']is None)
        else:
            successful=[v for v in prior if v['status']=='SUCCESS']
            require(len(successful)==1 and successful[0]['run_id']==OLD_RUN and instant(successful[0]['ended_at'])<=instant(r['started_at']))
            require(r['status']=='SKIPPED'and r['error_code']=='ALREADY_SUCCESSFUL'and r['error_summary']=='step already successful for business date')
            require(r['ended_at']==r['started_at']and all(r[k]==0 for k in ('target_count','success_count','failure_count','byte_count')))
    require(rows['BACKUP_DB']['started_at']==rows['BACKUP_CONFIG']['started_at']and rows['BACKUP_DB']['ended_at']==rows['BACKUP_CONFIG']['ended_at'])
    return {'oldBatchRowsPreserved':472,'newBackupSuccessSteps':2,'newDomainAlreadySuccessfulSkips':8,'allNewRowsFull17ColumnsVerified':True,'actualTestSkippedCount':0,'wholeFormalAccepted':False}
