"""Literal new-day notification/session/Inbox/HTTP vectors, no Production expected generator."""
import copy
import unittest
from pyflakes.api import check,checkPath
from pg2078_current_same_day_rows_oracle_test import SameDay,RUN,CUT,UPPER
import pg4632_current_new_day_rows_oracle as oracle


def fixture():
    before,after=SameDay().fixture()
    for row in before['schubert.batch_runs']:row['business_date']='2026-10-12'
    for row in after['schubert.batch_runs'][:10]:row['business_date']='2026-10-12'
    before['schubert.notifications']=[{'id':31,'question_id':11,'state':'CANCELLED','state_changed_at':'2026-10-13T03:08:18.452472Z'},
      {'id':32,'question_id':11,'state':'CANCELLED','state_changed_at':CUT}]
    after['schubert.notifications']=[copy.deepcopy(before['schubert.notifications'][1])]
    before['schubert.auth_sessions']=[{'id':'expired-immutable','expires_at':'2026-10-12T03:08:18.452473Z','revoked':False,'revoked_at':None}]
    after['schubert.auth_sessions']=[]
    before['schubert.request_inbox'][0]['result_ref_uuid']='expired-immutable'
    after['schubert.request_inbox'][0]['result_ref_uuid']='expired-immutable'
    after['schubert_web_session.web_http_sessions']=[after['schubert_web_session.web_http_sessions'][-1]]
    for row in after['schubert.batch_runs'][10:]:
        row['attempt']=1
        if row['step'].startswith('BACKUP')or row['step']=='CLEAN_INBOX_OUTBOX':continue
        row.update(status='SUCCESS',error_code=None,error_summary=None,target_count=1 if row['step']=='CLEAN_NOTIFICATION'else 2 if row['step']=='CLEAN_SESSION'else 0,success_count=1 if row['step']=='CLEAN_NOTIFICATION'else 2 if row['step']=='CLEAN_SESSION'else 0)
    after['schubert.log_cleanup_progress']=[{'run_id':RUN,'cutoff':CUT,'completed_at':'2026-10-13T03:09:00Z','target_count':0,'deleted_count':0,'skipped_count':0,'after_logged_at':None,'after_id':None}]
    return before,after


class NewDay(unittest.TestCase):
    def test_literal_new_day_and_session_cleanup_precedes_inbox_validation(self):
        result=oracle.qualify(*fixture(),RUN,CUT,UPPER)
        self.assertEqual((10,2,1,0,1),(result['newDaySteps'],result['expectedSessionDeleted'],result['expectedOutboxDeleted'],result['expectedInboxDeleted'],result['expectedInboxProtected']))
        self.assertEqual(1,result['newAnonymousHttpLogs']);self.assertEqual(1,result['newAnonymousSessions']);self.assertEqual(1,result['newSentOutbox'])
        self.assertEqual(result,oracle.qualify_current(*fixture(),RUN,CUT,UPPER))

    def test_wrong_business_day_attempt_counts_deletion_and_status_refused(self):
        before,after=fixture()
        for key,value in [('business_date','2026-10-14'),('attempt',2),('id',True),('failure_count',1),('status','SKIPPED'),('run_id','foreign')]:
            bad=copy.deepcopy(after);bad['schubert.batch_runs'][12][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):oracle.qualify(before,bad,RUN,CUT,UPPER)
        for table in ['schubert.notifications','schubert.auth_sessions','schubert_web_session.web_http_sessions','schubert_web_session.web_log_outbox']:
            bad=copy.deepcopy(after);bad[table].append(copy.deepcopy(before[table][0]))
            with self.subTest(table=table),self.assertRaises(ValueError):oracle.qualify(before,bad,RUN,CUT,UPPER)
        bad=copy.deepcopy(after);bad['schubert.notifications']=[]
        with self.assertRaises(ValueError):oracle.qualify(before,bad,RUN,CUT,UPPER)

    def test_same_day_partial_history_unknown_inbox_and_missing_schema_refused(self):
        before,after=fixture()
        for mutate in [lambda v:v['schubert.batch_runs'][0].update(business_date='2026-10-13'),lambda v:v['schubert.request_inbox'][0].update(request_layout_id='UNKNOWN'),lambda v:v['schubert.auth_sessions'][0].update(expires_at='2026-10-12T03:08:18.452474Z'),lambda v:v.pop('schubert.questions')]:
            bad=copy.deepcopy(before);mutate(bad)
            with self.assertRaises(ValueError):oracle.qualify(bad,after,RUN,CUT,UPPER)
        for value in [None,{},dict(before,invented=[])]:
            with self.assertRaises(ValueError):oracle.qualify(value,after,RUN,CUT,UPPER)

    def test_full_emitted_source_has_no_business_oracle_dependency(self):
        raw=oracle.source();self.assertEqual(0,check(raw,'<new day full24 independent oracle>'))
        self.assertEqual(0,checkPath('tools/quality/pg4632_current_new_day_rows_oracle.py'))
        self.assertIn("targets={'CLEAN_NOTIFICATION':len(expected['notifications'])",raw)
        self.assertNotIn("r['business_date']=='2026-10-13'",raw)
        self.assertNotIn('dev.codex.schubert.nk.',raw)


if __name__=='__main__':unittest.main()
