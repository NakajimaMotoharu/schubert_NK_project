"""Independent ten-step/durable rows fixture; no production execution generates expectations."""
import copy
import unittest
from pg2023_fresh_resume_rows_oracle import qualify,payload

RUN='4148e3e8-f107-431a-ab27-d6e6d1f1772e'
CUT='2026-10-12T18:20:32.598894Z'
LOW='2026-10-13T01:15:32Z';HIGH='2026-10-13T01:45:32Z'
STEPS=['BACKUP_DB','BACKUP_CONFIG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER','CLEAN_EXPIRY']


class Rows(unittest.TestCase):
    def fixture(self):
        old={**{'fixture.table'+str(i):[]for i in range(19)},'schubert.batch_runs':[{'run_id':RUN,'step':s,'attempt':1}for s in STEPS],'schubert.app_logs':[],'schubert_web_session.web_http_sessions':[],'schubert_web_session.web_log_outbox':[],'schubert.inbox_inspection_progress':[{'run_id':RUN,'cutoff':CUT,'protected_count':4,'completed_at':'2026-10-12T18:40:00Z'}]}
        new=copy.deepcopy(old)
        for index,step in enumerate(STEPS):
            warning=step=='CLEAN_INBOX_OUTBOX'
            new['schubert.batch_runs'].append({'id':index+100,'run_id':RUN,'business_date':'2026-10-13','step':step,'attempt':2,'status':'WARNING'if warning else'SKIPPED','error_code':'PROTECTED_RECORDS'if warning else'ALREADY_SUCCESSFUL','error_summary':'protected records retained'if warning else'step already successful for business date','target_count':0,'success_count':0,'failure_count':0,'byte_count':0,'started_at':'2026-10-13T01:16:00Z','ended_at':'2026-10-13T01:16:00Z'})
        for i in range(2):
            uid='00000000-0000-4000-8000-00000000000'+str(i+1)
            new['schubert.app_logs'].append({'id':i+1,'source_message_id':uid,'message_id':uid,'correlation_id':uid,'service':'WEB','category':'REQUEST','level':'INFO','action':'HTTP_REQUEST_COMPLETED','http_method':'GET','status_code':200,'request_uri':'/login','actor_user_id':None,'actor_username':None,'security_hold_until':None,'logged_at':'2026-10-13T01:25:00Z','message':'HTTP request complete','details':{},'duration_ms':1})
            new['schubert_web_session.web_log_outbox'].append({'message_id':uid,'correlation_id':uid,'layout_id':'WLGEVT01','layout_version':'001','status':'SENT','last_error_code':None,'lease_owner':None,'lease_until':None,'attempt_count':1,'created_at':'2026-10-13T01:25:00Z','sent_at':'2026-10-13T01:25:01Z','payload_ciphertext':'\\x'+'ab'*29,'key_version':'v1'})
            new['schubert_web_session.web_http_sessions'].append({'id':uid,'key_version':'v1','attributes_ciphertext':'\\x'+'ab'*29,'session_id_hash':'a'*64,'max_inactive_seconds':1800,'version':1,'created_at':'2026-10-13T01:25:00Z','last_accessed_at':'2026-10-13T01:25:00Z','expires_at':'2026-10-13T01:55:00Z'})
        return old,new

    def test_all_old_rows_retained_nine_skips_warning_and_http(self):
        old,new=self.fixture();result=qualify(old,new,RUN,CUT,LOW,HIGH)
        self.assertEqual((9,1,2,2),(result['newSkippedSteps'],result['newProtectedWarningSteps'],result['newAnonymousHttpLogs'],result['newSentOutbox']))
        payload()

    def test_no_old_delete_change_or_progress_reset(self):
        old,new=self.fixture()
        for table in ['schubert.batch_runs','schubert.inbox_inspection_progress']:
            bad=copy.deepcopy(new);bad[table].pop(0)
            with self.assertRaises(ValueError):qualify(old,bad,RUN,CUT,LOW,HIGH)
        bad=copy.deepcopy(new);bad['schubert.inbox_inspection_progress'][0]['protected_count']=0
        with self.assertRaises(ValueError):qualify(old,bad,RUN,CUT,LOW,HIGH)

    def test_reexecution_wrong_attempt_status_counts_and_unsent_rejected(self):
        old,new=self.fixture()
        for key,value in [('status','SUCCESS'),('attempt',1),('target_count',1),('run_id','foreign'),('business_date','2026-10-14')]:
            bad=copy.deepcopy(new);bad['schubert.batch_runs'][-1][key]=value
            with self.assertRaises(ValueError):qualify(old,bad,RUN,CUT,LOW,HIGH)
        bad=copy.deepcopy(new);bad['schubert_web_session.web_log_outbox'][0]['status']='PENDING'
        with self.assertRaises(ValueError):qualify(old,bad,RUN,CUT,LOW,HIGH)


if __name__=='__main__':unittest.main()
