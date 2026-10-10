import copy
import unittest
from pg1196_completed_rows_oracle import after, output_bound, LIMIT


class CompletedRowsTest(unittest.TestCase):
    def fixture(self):
        old={k:[]for k in ['schubert.batch_runs','schubert.app_logs','schubert_web_session.web_http_sessions','schubert_web_session.web_log_outbox',*[f'schubert.fixture_{n}'for n in range(20)]]}
        new=copy.deepcopy(old);run='11111111-1111-4111-8111-111111111111';event='22222222-2222-4222-8222-222222222222';time='2026-10-10T17:16:00+00:00'
        for step in ['BACKUP_DB','BACKUP_CONFIG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER','CLEAN_EXPIRY']:
            new['schubert.batch_runs'].append(dict(step=step,run_id=run,business_date='2026-10-10',status='SKIPPED',error_code='ALREADY_SUCCESSFUL',error_summary='step already successful for business date',target_count=0,success_count=0,failure_count=0,byte_count=0,started_at=time,ended_at=time))
        new['schubert.app_logs']=[dict(source_message_id=event,message_id=event,correlation_id=event,service='WEB',category='REQUEST',level='INFO',action='HTTP_REQUEST_COMPLETED',http_method='GET',status_code=200,request_uri='/login',actor_user_id=None,actor_username=None,security_hold_until=None,logged_at=time,message='literal request completion',details={},duration_ms=1)]
        new['schubert_web_session.web_log_outbox']=[dict(message_id=event,correlation_id=event,layout_id='WLGEVT01',layout_version='001',status='SENT',last_error_code=None,lease_owner=None,lease_until=None,attempt_count=1,created_at=time,sent_at=time,payload_ciphertext='\\x'+'ab'*29,key_version='fixture-v1')]
        new['schubert_web_session.web_http_sessions']=[dict(id='33333333-3333-4333-8333-333333333333',session_id_hash='a'*64,attributes_ciphertext='\\x'+'cd'*29,key_version='fixture-v1',max_inactive_seconds=1800,version=0,created_at=time,last_accessed_at=time,expires_at='2026-10-10T17:46:00+00:00')]
        return old,new,run,'2026-10-10T17:15:39+00:00','2026-10-10T18:00:00+00:00'

    def test_independent_literal_complete_same_snapshot_delta(self):
        v=after(*self.fixture());self.assertEqual(v['newSkippedSteps'],10);self.assertEqual(v['newAnonymousHttpLogs'],1);self.assertTrue(v['logOutboxOneToOne']);self.assertFalse(v['wholeAccepted'])

    def test_finite_size_boundary_code_type_empty_and_overflow(self):
        for size in [1,33554432,34115986,LIMIT]:output_bound(0,size)
        for code,size in [(1,1),(0,0),(0,LIMIT+1),(0,None),(None,1),(True,1),(0,True),(0,-1)]:
            with self.assertRaises(ValueError):output_bound(code,size)

    def test_unknown_table_old_row_loss_batch_duplicate_wrong_run_and_counts(self):
        args=self.fixture()
        for table,key,value in [('schubert.batch_runs','run_id','44444444-4444-4444-8444-444444444444'),('schubert.batch_runs','status','SUCCESS'),('schubert.batch_runs','success_count',1),('schubert.app_logs','request_uri','/foreign'),('schubert.app_logs','status_code',500),('schubert.app_logs','actor_username','foreign'),('schubert_web_session.web_log_outbox','status','PENDING'),('schubert_web_session.web_log_outbox','payload_ciphertext',None),('schubert_web_session.web_http_sessions','session_id_hash',None),('schubert_web_session.web_http_sessions','max_inactive_seconds',True)]:
            v=copy.deepcopy(args);v[1][table][0][key]=value
            with self.subTest(table=table,key=key),self.assertRaises(ValueError):after(*v)
        v=copy.deepcopy(args);v[0]['schubert.fixture_0']=[{'id':1}]
        with self.assertRaises(ValueError):after(*v)
        v=copy.deepcopy(args);v[1]['schubert.fixture_0']=[{'id':2}]
        with self.assertRaises(ValueError):after(*v)

    def test_null_unknown_duplicate_or_missing_projection_and_time_rejected(self):
        args=self.fixture()
        for index in [0,1]:
            v=list(args);v[index]=None
            with self.assertRaises(ValueError):after(*v)
        for table in ['schubert.app_logs','schubert_web_session.web_log_outbox']:
            v=copy.deepcopy(args);v[1][table]=[]
            with self.assertRaises(ValueError):after(*v)
            v=copy.deepcopy(args);v[1][table]+=v[1][table]
            with self.assertRaises(ValueError):after(*v)
        v=copy.deepcopy(args);v[1]['schubert.batch_runs'][0]['ended_at']='2026-10-10T17:17:00+00:00'
        with self.assertRaises(ValueError):after(*v)


if __name__=='__main__':unittest.main()
