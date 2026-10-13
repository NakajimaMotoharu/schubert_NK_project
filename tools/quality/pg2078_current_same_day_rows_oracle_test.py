"""Independent literal same-day history, backup counters, cutoff selectors and protected snapshot."""
import copy
import unittest
from pg2078_current_same_day_rows_oracle import qualify,source

RUN='a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75'
CUT='2026-10-13T03:08:18.452473Z'
UPPER='2026-10-13T03:40:00Z'
STEPS=['BACKUP_DB','BACKUP_CONFIG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER','CLEAN_EXPIRY']


class SameDay(unittest.TestCase):
    def fixture(self):
        tables=['notifications','questions','auth_sessions','login_ip_attempts','mq_outbox','app_logs','batch_runs','inbox_inspection_progress','log_cleanup_progress','request_inbox','app_users']
        old={**{'schubert.'+n:[]for n in tables},**{'schubert_web_session.'+n:[]for n in ['web_http_sessions','web_log_outbox','web_receipt_references']},**{'fixture.table'+str(i):[]for i in range(10)}}
        for i,s in enumerate(STEPS):old['schubert.batch_runs'].append({'id':i+1,'run_id':'previous','business_date':'2026-10-13','step':s,'attempt':2,'status':'WARNING'if s=='CLEAN_INBOX_OUTBOX'else'SUCCESS','ended_at':'2026-10-13T02:00:00Z'})
        mid='00000000-0000-4000-8000-000000000099'
        old['schubert.request_inbox']=[dict(message_id=mid,request_layout_id='LGNREQ01',response_layout_id='LGNRSP01',processing_state='COMPLETED',result_ref_type='AUTH_SESSION',owner_user_id=None,result_ref_uuid='missing-session',expires_at='2026-10-13T00:00:00Z')]
        old['schubert_web_session.web_log_outbox']=[dict(id=1,status='SENT',sent_at='2026-10-06T00:00:00Z',lease_until=None)]
        old['schubert_web_session.web_http_sessions']=[dict(id='retained-expired',expires_at='2026-10-13T01:00:00Z')]
        new=copy.deepcopy(old);new['schubert_web_session.web_log_outbox']=[]
        for i,s in enumerate(STEPS):
            backup=s.startswith('BACKUP');warning=s=='CLEAN_INBOX_OUTBOX'
            count=1 if s=='BACKUP_DB'else 2 if s=='BACKUP_CONFIG'else 2 if warning else 0
            new['schubert.batch_runs'].append(dict(id=i+100,run_id=RUN,business_date='2026-10-13',step=s,attempt=3,status='SUCCESS'if backup else'WARNING'if warning else'SKIPPED',target_count=count,success_count=1 if warning else count,failure_count=0,byte_count=123 if backup else 0,error_code=None if backup else'PROTECTED_RECORDS'if warning else'ALREADY_SUCCESSFUL',error_summary=None if backup else'protected records retained'if warning else'step already successful for business date',started_at='2026-10-13T03:09:00Z',ended_at='2026-10-13T03:09:00Z'))
        new['schubert.inbox_inspection_progress']=[dict(run_id=RUN,cutoff=CUT,completed_at='2026-10-13T03:09:00Z',inspected_count=1,deleted_count=0,protected_count=1,after_message_id=mid)]
        event='00000000-0000-4000-8000-000000000001';time='2026-10-13T03:10:00Z'
        new['schubert.app_logs']=[dict(id=1,source_message_id=event,message_id=event,correlation_id=event,service='WEB',category='REQUEST',level='INFO',action='HTTP_REQUEST_COMPLETED',http_method='GET',status_code=200,request_uri='/login',actor_user_id=None,actor_username=None,security_hold_until=None,logged_at=time,message='literal completion',details={},duration_ms=1)]
        new['schubert_web_session.web_log_outbox']=[dict(id=2,message_id=event,correlation_id=event,layout_id='WLGEVT01',layout_version='001',status='SENT',last_error_code=None,lease_owner=None,lease_until=None,attempt_count=1,created_at=time,sent_at=time,payload_ciphertext='\\x'+'ab'*29,key_version='v1')]
        new['schubert_web_session.web_http_sessions'].append(dict(id=event,key_version='v1',attributes_ciphertext='\\x'+'ab'*29,session_id_hash='a'*64,max_inactive_seconds=1800,version=1,created_at=time,last_accessed_at=time,expires_at='2026-10-13T03:40:00Z'))
        return old,new

    def test_literal_backup_every_run_skip_history_and_cutoff_outbox(self):
        result=qualify(*self.fixture(),RUN,CUT,UPPER)
        self.assertEqual((2,7,1,1),(result['newBackupSteps'],result['newSkippedSteps'],result['expectedInboxProtected'],result['expectedOutboxDeleted']))
        ns={};exec(source(),ns)
        self.assertEqual(result,ns['qualify'](*self.fixture(),RUN,CUT,UPPER))

    def test_reexecution_wrong_counts_attempt_deletion_and_unknown_rejected(self):
        old,new=self.fixture()
        for key,value in [('attempt',2),('id',True),('target_count',1),('status','SUCCESS'),('run_id','other'),('business_date','2026-10-14')]:
            bad=copy.deepcopy(new);bad['schubert.batch_runs'][-1][key]=value
            with self.assertRaises(ValueError):qualify(old,bad,RUN,CUT,UPPER)
        for table in ['schubert.request_inbox','schubert_web_session.web_http_sessions']:
            bad=copy.deepcopy(new);bad[table].pop(0)
            with self.assertRaises(ValueError):qualify(old,bad,RUN,CUT,UPPER)
        bad=copy.deepcopy(new);bad['schubert_web_session.web_log_outbox']+=old['schubert_web_session.web_log_outbox']
        with self.assertRaises(ValueError):qualify(old,bad,RUN,CUT,UPPER)
        bad=copy.deepcopy(new);bad['schubert.inbox_inspection_progress'][0]['protected_count']=0
        with self.assertRaises(ValueError):qualify(old,bad,RUN,CUT,UPPER)


if __name__=='__main__':unittest.main()
