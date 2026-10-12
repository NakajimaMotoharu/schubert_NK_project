"""Hand-written DDL/SS fixtures: new skip rows, HTTP redaction and resend bijection."""
import copy
import unittest
from pg1602_current_newrun_rows_oracle import qualify

class NewRunSqlOracleTest(unittest.TestCase):
    def fixture(self):
        before={name:[]for name in ['schubert.batch_runs','schubert.app_logs','schubert_web_session.web_http_sessions','schubert_web_session.web_log_outbox',*['schubert.fixture_'+str(i)for i in range(20)]]}
        steps=['BACKUP_DB','BACKUP_CONFIG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER','CLEAN_EXPIRY']
        for i,step in enumerate(steps):
            before['schubert.batch_runs'].append({'id':i+1,'run_id':'15700a87-9117-4f63-a0ff-768dd604d0f1','business_date':'2026-10-12','step':step,'attempt':1,'status':'SUCCESS'})
        after=copy.deepcopy(before)
        for i,step in enumerate(steps):
            after['schubert.batch_runs'].append({'id':11+i,'run_id':'0be226b1-bbb7-43d3-aa9e-59d0bda70f9a','business_date':'2026-10-12','step':step,'attempt':2,'status':'SKIPPED','error_code':'ALREADY_SUCCESSFUL','error_summary':'step already successful for business date','target_count':0,'success_count':0,'failure_count':0,'byte_count':0,'started_at':'2026-10-12T06:24:00Z','ended_at':'2026-10-12T06:24:00Z'})
        event='11111111-1111-4111-8111-111111111111';cipher='\\x'+'ab'*32
        after['schubert_web_session.web_log_outbox']=[{'message_id':event,'correlation_id':event,'layout_id':'WLGEVT01','layout_version':'001','status':'SENT','last_error_code':None,'lease_owner':None,'lease_until':None,'attempt_count':0,'created_at':'2026-10-12T06:40:00Z','sent_at':'2026-10-12T06:40:01Z','payload_ciphertext':cipher,'key_version':'v1'}]
        after['schubert.app_logs']=[{'source_message_id':event,'message_id':event,'correlation_id':event,'service':'WEB','category':'REQUEST','level':'INFO','action':'HTTP_REQUEST_COMPLETED','http_method':'GET','status_code':200,'request_uri':'/login','actor_user_id':None,'actor_username':None,'security_hold_until':None,'logged_at':'2026-10-12T06:40:00Z','message':'HTTP completed','details':{},'duration_ms':1}]
        after['schubert_web_session.web_http_sessions']=[{'id':'22222222-2222-4222-8222-222222222222','key_version':'v1','attributes_ciphertext':cipher,'session_id_hash':'a'*64,'max_inactive_seconds':60,'version':0,'created_at':'2026-10-12T06:40:00Z','last_accessed_at':'2026-10-12T06:40:00Z','expires_at':'2026-10-12T06:41:00Z'}]
        return before,after

    def test_literal_success_and_replay_ownership_cipher_negative(self):
        old,new=self.fixture();start='2026-10-12T06:23:13.176261Z';end='2026-10-12T06:45:00Z'
        v=qualify(old,new,start,end);self.assertEqual(v['newSkippedSteps'],10);self.assertEqual(v['newAnonymousHttpLogs'],1);self.assertFalse(v['oldCompletedRunResumed'])
        for key,bad in [('run_id','15700a87-9117-4f63-a0ff-768dd604d0f1'),('attempt',1),('status','SUCCESS'),('business_date','2026-10-11'),('byte_count',1),('id',1)]:
            changed=copy.deepcopy(new);changed['schubert.batch_runs'][-1][key]=bad
            with self.assertRaises(ValueError):qualify(old,changed,start,end)
        for table,key,bad in [('schubert.app_logs','actor_username','raw user'),('schubert.app_logs','source_message_id','33333333-3333-4333-8333-333333333333'),('schubert_web_session.web_log_outbox','lease_owner','still-owned'),('schubert_web_session.web_log_outbox','status','PENDING'),('schubert_web_session.web_http_sessions','attributes_ciphertext','raw plaintext'),('schubert_web_session.web_http_sessions','session_id_hash','raw-id')]:
            changed=copy.deepcopy(new);changed[table][0][key]=bad
            with self.assertRaises(ValueError):qualify(old,changed,start,end)
        for bad in [None,{},dict(new,**{'schubert.fixture_0':[{'unapproved':'row'}]})]:
            with self.assertRaises(ValueError):qualify(old,bad,start,end)

if __name__=='__main__':unittest.main()
