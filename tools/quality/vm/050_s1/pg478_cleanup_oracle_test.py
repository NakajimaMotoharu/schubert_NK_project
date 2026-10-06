"""Literal time/FK/protection vectors independent of production methods and live DB."""
from pg478_cleanup_oracle import candidates,instant,older
tables=['schubert.'+t for t in ['notifications','questions','auth_sessions','login_ip_attempts','mq_outbox','app_logs','batch_runs','inbox_inspection_progress','log_cleanup_progress','request_inbox']]+['schubert_web_session.'+t for t in ['web_http_sessions','web_log_outbox','web_receipt_references']]
rows={t:[] for t in tables};c='2026-10-06T06:00:00+00:00';checks=0
def check(v):
 global checks
 checks+=1;assert v
check(all(not x for x in candidates(rows,c).values()))
check(instant('2026-10-06T15:00:00+09:00')==instant(c));check(not older(None,instant(c)))
for bad in ['2026-10-06T06:00:00','not-time']:
 try:instant(bad)
 except ValueError:checks+=1
 else:raise AssertionError('bad timezone accepted')
rows['schubert_web_session.web_http_sessions']=[{'id':str(i),'expires_at':x} for i,x in enumerate(['2026-10-06T05:59:59Z',c,'2026-10-06T06:00:00.000001Z'])]
check(candidates(rows,c)['web_http_sessions']==['0','1'])
rows['schubert.auth_sessions']=[{'id':'a','expires_at':'2026-10-05T06:00:00Z','revoked':False,'revoked_at':None},{'id':'b','expires_at':c,'revoked':True,'revoked_at':'2026-10-05T05:59:59Z'},{'id':'c','expires_at':c,'revoked':False,'revoked_at':None}]
check(candidates(rows,c)['auth_sessions']==['a','b'])
rows['schubert.notifications']=[{'id':'n','question_id':'q','state':'PENDING','state_changed_at':'2026-01-01T00:00:00Z'}]
rows['schubert.questions']=[{'id':'q','is_deleted':True,'deleted_at':'2026-10-05T00:00:00Z'}]
check(candidates(rows,c)['questions']==[])
rows['schubert.notifications'][0]['state']='CANCELLED';check(candidates(rows,c)['notifications']==['n']);check(candidates(rows,c)['questions']==['q'])
for table in ['schubert.mq_outbox','schubert_web_session.web_log_outbox']:
 rows[table]=[{'id':'old','status':'SENT','sent_at':'2026-09-29T05:59:59Z','lease_until':None},{'id':'edge','status':'SENT','sent_at':'2026-09-29T06:00:00Z','lease_until':None},{'id':'pending','status':'PENDING','sent_at':'2026-01-01T00:00:00Z','lease_until':None},{'id':'lease','status':'SENT','sent_at':'2026-01-01T00:00:00Z','lease_until':c}]
 check(candidates(rows,c)[table]==['old'])
rows['schubert.app_logs']=[{'id':'free','logged_at':'2020-01-01T00:00:00Z','security_hold_until':None},{'id':'held','logged_at':'2020-01-01T00:00:00Z','security_hold_until':c}]
check(candidates(rows,c)['app_logs']==['free'])
rows['schubert.batch_runs']=[{'id':'success','run_id':'run','status':'SUCCESS','ended_at':'2020-01-01T00:00:00Z'},{'id':'failed','run_id':'run','status':'FAILED','ended_at':'2020-01-01T00:00:00Z'}]
check(candidates(rows,c)['batch_runs']==[]);rows['schubert.batch_runs'].pop();check(candidates(rows,c)['batch_runs']==['success'])
rows['schubert.request_inbox']=[{'message_id':'m','processing_state':'COMPLETED','expires_at':'2026-10-06T05:59:59Z'},{'message_id':'p','processing_state':'PROCESSING','expires_at':'2020-01-01T00:00:00Z'}]
check(candidates(rows,c)['inbox_scan_candidates']==['m'])
rows['schubert_web_session.web_receipt_references']=[{'receipt_id':'orphan','question_id':'missing'},{'receipt_id':'kept','question_id':'kept'}]
rows['schubert.questions'].append({'id':'kept','is_deleted':False,'deleted_at':None})
check(candidates(rows,c)['web_receipt_references']==['orphan'])
rows['schubert.login_ip_attempts']=[{'client_address':'ip','window_started_at':'2026-10-05T05:45:00Z','locked_until':None},{'client_address':'held','window_started_at':'2020-01-01T00:00:00Z','locked_until':c}]
check(candidates(rows,c)['login_ip_attempts']==['ip'])
for table in ['schubert.inbox_inspection_progress','schubert.log_cleanup_progress']:
 rows[table]=[{'run_id':'old','completed_at':'2020-01-01T00:00:00Z'},{'run_id':'pending','completed_at':None}]
 check(candidates(rows,c)[table]==['old'])
print('PG478_CLEANUP_ORACLE_TEST independentAssertions='+str(checks)+' privateDataRead0=true productionPT0=true')
