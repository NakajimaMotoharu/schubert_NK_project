"""Independent old-cutoff full-row survivor oracle. Not parent/whole-run acceptance."""
import datetime,json
RUN='49437eda-1681-43a9-883a-424eb55a6166';CUTOFF='2026-10-06T06:28:43.734078+00:00'
SELECTORS={'schubert.notifications':('notifications','id'),'schubert.questions':('questions','id'),'schubert.auth_sessions':('auth_sessions','id'),'schubert.login_ip_attempts':('login_ip_attempts','client_address'),'schubert_web_session.web_http_sessions':('web_http_sessions','id'),'schubert.mq_outbox':('schubert.mq_outbox','id'),'schubert_web_session.web_log_outbox':('schubert_web_session.web_log_outbox','id'),'schubert.app_logs':('app_logs','id'),'schubert_web_session.web_receipt_references':('web_receipt_references','receipt_id')}
GENERATED={'schubert.batch_runs','schubert.inbox_inspection_progress','schubert.log_cleanup_progress'}
def require(value):
 if not value:raise ValueError('independent cleanup postcondition mismatch')
def canonical(rows):
 require(isinstance(rows,list) and all(isinstance(r,dict) and r for r in rows))
 values=[json.dumps(r,sort_keys=True,separators=(',',':')) for r in rows];require(len(values)==len(set(values)));return sorted(values)
def survivors(rows,deleted,key):
 require(isinstance(deleted,list) and all(isinstance(v,str) and v for v in deleted) and len(deleted)==len(set(deleted)))
 canonical(rows);require(all(key in r and r[key] is not None for r in rows))
 ids=[str(r[key]) for r in rows];require(len(ids)==len(set(ids)) and set(deleted)<=set(ids))
 return [r for r in rows if str(r[key]) not in set(deleted)]
def evaluate(old,new,oracle):
 require(isinstance(old,dict) and isinstance(new,dict) and set(old)==set(new) and len(old)==24)
 require(oracle['sameThroughoutAdmissionWindow'] and len(oracle['inboxExpectedDeleted'])==7 and len(oracle['expected']['auth_sessions'])==1 and len(oracle['expected']['web_http_sessions'])==1381)
 result={}
 for table,rows in old.items():
  actual=new[table]
  if table in GENERATED:
   key='id' if table=='schubert.batch_runs' else 'run_id'
   old_ids={str(r[key]) for r in rows};require(canonical(rows)==canonical([r for r in actual if str(r[key]) in old_ids]))
   added=[r for r in actual if str(r[key]) not in old_ids];require(all(r['run_id']==RUN for r in added));result[table]={'oldPreserved':len(rows),'addedObserved':len(added),'newRowsNotFinalAccepted':True};continue
  if table=='schubert.request_inbox':expected=survivors(rows,oracle['inboxExpectedDeleted'],'message_id')
  elif table in SELECTORS:
   selector,key=SELECTORS[table];expected=survivors(rows,oracle['expected'][selector],key)
  else:expected=rows
  require(canonical(expected)==canonical(actual));result[table]={'before':len(rows),'after':len(actual),'deleted':len(rows)-len(actual),'allSurvivorColumnsEqual':True}
 return result
