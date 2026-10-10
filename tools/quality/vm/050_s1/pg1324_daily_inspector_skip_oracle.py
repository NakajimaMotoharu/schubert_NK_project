"""Independent SS3318.3/SS341SSC200 daily Inspector skip and preserved progress."""
import datetime
import uuid

FIELDS={'id','run_id','business_date','step','attempt','started_at','ended_at','status','target_count','success_count','failure_count','byte_count','error_code','error_summary'}


def require(value):
    if not value:raise ValueError('daily Inspector independent skip refused')


def instant(value):
    require(type(value)is str and value.endswith(('Z','+00:00')))
    parsed=datetime.datetime.fromisoformat(value.replace('Z','+00:00'))
    require(parsed.tzinfo is not None);return parsed


def qualify(old,new,run,cutoff,upper,old_native,new_native):
    require(type(old)is dict and type(new)is dict and type(run)is str and isinstance(cutoff,datetime.datetime)and isinstance(upper,datetime.datetime)and cutoff.tzinfo is not None and upper.tzinfo is not None and cutoff<=upper)
    value=uuid.UUID(run);require(str(value)==run and value.version==4)
    day=cutoff.astimezone(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()
    table='schubert.batch_runs';progress='schubert.inbox_inspection_progress'
    require(type(old.get(table))is list and type(new.get(table))is list and type(old.get(progress))is list and type(new.get(progress))is list)
    require(all(type(row)is dict and set(row)==FIELDS for row in old[table]+new[table]))
    require(all(row in new[table]for row in old[table]))
    original=[r for r in old[table]if r['business_date']==day and r['step']=='CLEAN_INBOX_OUTBOX'and r['status']=='SUCCESS']
    require(len(original)==1 and original[0]['run_id']!=run)
    prior=original[0];require(type(prior['attempt'])is int and prior['attempt']>0 and instant(prior['started_at'])<=instant(prior['ended_at'])<=cutoff)
    expected_attempt=max(r['attempt']for r in old[table]if r['business_date']==day and r['step']=='CLEAN_INBOX_OUTBOX')+1
    rows=[r for r in new[table]if r not in old[table]and r['run_id']==run and r['step']=='CLEAN_INBOX_OUTBOX']
    require(len(rows)==1);row=rows[0]
    require(row['business_date']==day and row['status']=='SKIPPED'and row['error_code']=='ALREADY_SUCCESSFUL'and row['error_summary']=='step already successful for business date')
    require(type(row['id'])is int and row['id']>prior['id']and type(row['attempt'])is int and row['attempt']==expected_attempt)
    require(row['started_at']==row['ended_at']and cutoff<=instant(row['started_at'])<=upper)
    require(all(type(row[k])is int and row[k]==0 for k in ['target_count','success_count','failure_count','byte_count']))
    require(new[progress]==old[progress])
    require(type(old_native)is dict and type(new_native)is dict)
    select=lambda v:{p:r for p,r in v.items()if '/ordinary-inspector196/'in p and p.endswith('.exec')}
    require(select(old_native)==select(new_native))
    return {'dailyInspectorSkipVerified':True,'independentExistingSuccessCount':1,'freshSkipRows':1,'freshInspectorExecutionInferred':False,'oldProgressAndNativePreserved':True,'newInspectorNativeAccepted':False}
