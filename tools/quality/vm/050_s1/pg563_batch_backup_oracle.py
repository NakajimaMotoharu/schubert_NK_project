"""SS341 independent new-run step/bundle oracle. No Production codec, raw data remains private."""
import datetime,hashlib,json,re
RUN='b7e73994-b951-4696-bdd1-cfbc8a10e734'
CUTOFF='2026-10-08T04:03:00.714124Z'
VERSIONS={'host':'pgpt-r2','app':'0.1.0-SNAPSHOT','schema':'028','os':'ubuntu-26.04','jdk':'25.0.4','postgresql':'18.6','artemis':'2.56.0','age':'1.2.1'}
STEPS=('BACKUP_DB','BACKUP_CONFIG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER','CLEAN_EXPIRY')
def require(v):
 if not v:raise ValueError('independent current batch backup oracle refused')
def time(value):
 require(type(value)is str);t=datetime.datetime.fromisoformat(value.replace('Z','+00:00'));require(t.tzinfo is not None);return t
def positive(n):return type(n)is int and 0<n<=9223372036854775807
def validate(old,new,oracle,raw_manifest,files):
 require(type(old)is dict and type(new)is dict and set(old)==set(new)and len(old)==24)
 before=old['schubert.batch_runs'];after=new['schubert.batch_runs'];require(type(before)is list and type(after)is list)
 old_ids={r['id']:r for r in before};require(len(old_ids)==len(before)and all(positive(k)for k in old_ids))
 actual={r['id']:r for r in after};require(len(actual)==len(after)and all(positive(k)for k in actual)and all(actual.get(k)==v for k,v in old_ids.items()))
 added=[v for k,v in actual.items()if k not in old_ids];require(len(added)==10 and {r['step']for r in added}==set(STEPS));rows={r['step']:r for r in added}
 require(type(raw_manifest)is bytes and 0<len(raw_manifest)<=4096)
 def unique(items):
  d={}
  for k,v in items:require(k not in d);d[k]=v
  return d
 m=json.loads(raw_manifest,object_pairs_hook=unique)
 require(list(m)==['format','database','runId','cutoff','startedAt','contentFinishedAt','databaseStep','configurationStep','versions','recipientSha256','files'])
 require(m['format']=='NKBACKUP1'and m['database']=='schubert_nk'and m['runId']==RUN and m['cutoff']==CUTOFF and m['versions']==VERSIONS and list(m['versions'])==list(VERSIONS))
 require(raw_manifest==(json.dumps(m,ensure_ascii=True,separators=(',',':'))+'\n').encode('ascii'))
 require(type(m['recipientSha256'])is str and re.fullmatch('[0-9a-f]{64}',m['recipientSha256'])is not None)
 require(type(files)is dict and set(files)=={'schubert_nk.dump','config.tar','credentials.tar.age'}and list(m['files'])==['schubert_nk.dump','config.tar','credentials.tar.age'])
 for name,data in files.items():
  claim=m['files'][name];require(type(claim)is dict and list(claim)==['size','sha256']and positive(claim['size']))
  require(type(data)is bytes and len(data)>0 and claim=={'size':len(data),'sha256':hashlib.sha256(data).hexdigest()})
 for value in (m['startedAt'],m['contentFinishedAt']):require(type(value)is str and re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z',value)is not None)
 start=time(m['startedAt']);finish=time(m['contentFinishedAt']);require(start>=time(CUTOFF)and finish>=start)
 for field,step in [('databaseStep','BACKUP_DB'),('configurationStep','BACKUP_CONFIG')]:
  claim=m[field];r=rows[step];require(type(claim)is dict and list(claim)==['id','attempt','startedAt']and positive(claim['id'])and positive(claim['attempt'])and claim['id']==r['id']and claim['attempt']==r['attempt']and time(claim['startedAt'])==time(r['started_at'])and time(r['started_at'])<=start and finish<=time(r['ended_at']))
 expected_counts={'BACKUP_DB':(1,len(files['schubert_nk.dump'])),'BACKUP_CONFIG':(2,len(files['config.tar'])+len(files['credentials.tar.age'])),'CLEAN_NOTIFICATION':(len(oracle['expected']['notifications']),0),'CLEAN_QUESTION':(len(oracle['expected']['questions']),0),'CLEAN_SESSION':(sum(len(oracle['expected'][s])for s in ('auth_sessions','login_ip_attempts','web_http_sessions')),0),'CLEAN_INBOX_OUTBOX':(len(oracle['inboxExpectedDeleted'])+sum(len(oracle['expected'][s])for s in ('schubert.mq_outbox','schubert_web_session.web_log_outbox')),0),'CLEAN_LOG':(len(oracle['expected']['app_logs']),0),'CLEAN_BATCH_RUN':(sum(len(oracle['expected'][s])for s in ('web_receipt_references','batch_runs','schubert.inbox_inspection_progress','schubert.log_cleanup_progress')),0),'CLEAN_TRANSFER':(0,0),'CLEAN_EXPIRY':(0,0)}
 for step,r in rows.items():
  require(set(r)=={'attempt','business_date','byte_count','ended_at','error_code','error_summary','expiry_after_count','expiry_before_count','expiry_cutoff_at','failure_count','id','run_id','started_at','status','step','success_count','target_count'})
  count,size=expected_counts[step];require(r['run_id']==RUN and r['business_date']=='2026-10-08'and r['status']=='SUCCESS'and positive(r['attempt']))
  previous=[v['attempt']for v in before if v['business_date']=='2026-10-08'and v['step']==step];require(r['attempt']==(max(previous)+1 if previous else 1))
  require(all(type(r[k])is int for k in ('target_count','success_count','failure_count','byte_count'))and (r['target_count'],r['success_count'],r['failure_count'],r['byte_count'])==(count,count,0,size))
  require(r['error_code']is None and r['error_summary']is None and time(CUTOFF)<=time(r['started_at'])<=time(r['ended_at']))
  if step=='CLEAN_EXPIRY':require(time(r['expiry_cutoff_at'])==time(CUTOFF)-datetime.timedelta(days=7)and type(r['expiry_before_count'])is int and type(r['expiry_after_count'])is int and r['expiry_before_count']==r['expiry_after_count']==0)
  else:require(r['expiry_cutoff_at']is None and r['expiry_before_count']is None and r['expiry_after_count']is None)
 return {'independentTenStepsVerified':True,'newBackupBothSuccessVerified':True,'oldBatchRowsPreserved':len(before),'stepCounts':{s:expected_counts[s][0]for s in STEPS},'manifestSha256':hashlib.sha256(raw_manifest).hexdigest(),'newRows114NotAcceptedHere':True}
