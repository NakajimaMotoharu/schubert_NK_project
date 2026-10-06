"""Independent SS331/332/341/UI251 retained-row selectors, never production SQL functions.
Raw database/identifiers are Root0600 only. Capture bounds first; actual cutoff must lie inside.
"""
import datetime,json,os,pathlib,sys
UTC=datetime.timezone.utc
def instant(value):
 if value is None:return None
 result=datetime.datetime.fromisoformat(value.replace('Z','+00:00'))
 if result.tzinfo is None:raise ValueError('timezone missing')
 return result.astimezone(UTC)
def older(value,cutoff,inclusive=False):
 t=instant(value);return t is not None and (t<=cutoff if inclusive else t<cutoff)
def candidates(rows,cutoff):
 c=instant(cutoff);assert c is not None
 h24=c-datetime.timedelta(hours=24);h168=c-datetime.timedelta(hours=168);d90=c-datetime.timedelta(days=90);d400=c-datetime.timedelta(days=400)
 ids=lambda table,test,key='id':sorted(str(r[key]) for r in rows[table] if test(r))
 result={}
 result['notifications']=ids('schubert.notifications',lambda r:(r['state']=='CANCELLED' and older(r['state_changed_at'],c)) or (r['state'] in ['COMPLETED','ERROR'] and older(r['state_changed_at'],h24,True)))
 remaining={str(r['question_id']) for r in rows['schubert.notifications'] if str(r['id']) not in result['notifications']}
 result['questions']=ids('schubert.questions',lambda r:r['is_deleted'] and older(r['deleted_at'],c) and str(r['id']) not in remaining)
 result['auth_sessions']=ids('schubert.auth_sessions',lambda r:older(r['expires_at'],h24,True) or (r['revoked'] and older(r['revoked_at'],h24,True)))
 def ip(r):
  window=instant(r['window_started_at'])+datetime.timedelta(minutes=15);locked=instant(r['locked_until']);return max(window,locked if locked else window)<=h24
 result['login_ip_attempts']=ids('schubert.login_ip_attempts',ip,'client_address')
 result['web_http_sessions']=ids('schubert_web_session.web_http_sessions',lambda r:older(r['expires_at'],c,True))
 for table in ['schubert.mq_outbox','schubert_web_session.web_log_outbox']:
  result[table]=ids(table,lambda r:r['status']=='SENT' and older(r['sent_at'],h168) and (r['lease_until'] is None or older(r['lease_until'],c)))
 result['app_logs']=ids('schubert.app_logs',lambda r:older(r['logged_at'],d90) and (r['security_hold_until'] is None or older(r['security_hold_until'],d90,True)))
 blocked={str(r['run_id']) for r in rows['schubert.batch_runs'] if r['status'] in ['RUNNING','FAILED']}
 result['batch_runs']=ids('schubert.batch_runs',lambda r:r['status'] in ['SUCCESS','WARNING','SKIPPED'] and older(r['ended_at'],d400) and str(r['run_id']) not in blocked)
 for table in ['schubert.inbox_inspection_progress','schubert.log_cleanup_progress']:
  result[table]=ids(table,lambda r:older(r['completed_at'],d400) and str(r['run_id']) not in blocked,'run_id')
 question_ids={str(r['id']) for r in rows['schubert.questions'] if str(r['id']) not in result['questions']}
 result['web_receipt_references']=ids('schubert_web_session.web_receipt_references',lambda r:str(r['question_id']) not in question_ids,'receipt_id')
 # Only scan candidates here; cryptographic/owner validity and actual progress are separate.
 result['inbox_scan_candidates']=ids('schubert.request_inbox',lambda r:r['processing_state'] in ['COMPLETED','ERROR'] and older(r['expires_at'],c),'message_id')
 return result
def main():
 assert os.geteuid()==0 and sys.argv[1:]==['capture']
 root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg478-newrun-preflight-v2');data=json.loads((root/'before.private.json').read_text())
 low=candidates(data['rows'],data['bounds']['lower']);high=candidates(data['rows'],data['bounds']['upper']);assert low==high,'cutoff-boundary candidates change'
 assert all(not v for k,v in low.items() if k!='web_http_sessions'),'additional independent business/Inspector oracle required before start'
 result={'bounds':data['bounds'],'expected':low,'sameThroughoutAdmissionWindow':True,'starts0':True}
 with (root/'cleanup-oracle.private.json').open('x') as f:os.fchmod(f.fileno(),0o600);json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
 print(json.dumps({'independentCandidateCounts':{k:len(v) for k,v in low.items()},'fullRowsPrivate':True,'starts0':True},sort_keys=True))
if __name__=='__main__':main()
