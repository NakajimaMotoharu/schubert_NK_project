import datetime
import unittest
from pg1243_fresh_day_rows_oracle import deleted_sessions, session_post, zero_progress_post

class FreshCleanupOracleTest(unittest.TestCase):
    def test_independent_inclusive_boundaries_and_locked_windows(self):
        cutoff = datetime.datetime(2026,10,10,20,3,22,718197,tzinfo=datetime.timezone.utc)
        limit = cutoff-datetime.timedelta(hours=24)
        at = lambda delta:(limit+datetime.timedelta(microseconds=delta)).isoformat()
        web = [{'id':n,'expires_at':(cutoff+datetime.timedelta(microseconds=n)).isoformat()} for n in [-1,0,1]]
        self.assertEqual(deleted_sessions('schubert_web_session.web_http_sessions',web,cutoff),web[:2])
        auth = [{'id':n,'expires_at':at(n),'revoked':False,'revoked_at':None} for n in [-1,0,1]]
        self.assertEqual(deleted_sessions('schubert.auth_sessions',auth,cutoff),auth[:2])
        revoked = dict(auth[2],revoked=True,revoked_at=at(0))
        self.assertEqual(deleted_sessions('schubert.auth_sessions',[revoked],cutoff),[revoked])
        ip = {'window_started_at':(limit-datetime.timedelta(minutes=15)).isoformat(),'locked_until':None}
        self.assertEqual(deleted_sessions('schubert.login_ip_attempts',[ip],cutoff),[ip])
        self.assertEqual(deleted_sessions('schubert.login_ip_attempts',[dict(ip,locked_until=at(1))],cutoff),[])
        names=['schubert.auth_sessions','schubert.login_ip_attempts','schubert_web_session.web_http_sessions','schubert.batch_runs','schubert.app_logs','schubert_web_session.web_log_outbox','schubert.inbox_inspection_progress','schubert.log_cleanup_progress']+[f'schubert.fixture_{i}'for i in range(16)]
        old={name:[] for name in names};old[names[0]]=auth;old[names[2]]=web
        new=dict(old);new[names[0]]=auth[2:];new[names[2]]=web[2:]
        self.assertEqual(session_post(old,new,cutoff)['expectedSessionDeletes'],4)
        for table in names:
            bad=dict(new);bad[table]=[{'unexpected':True}]
            if table not in names[3:8]:
                with self.assertRaises((ValueError,KeyError)):session_post(old,bad,cutoff)
        for bad in [None,[None],[{'expires_at':None}]]:
            with self.assertRaises(ValueError):deleted_sessions(names[2],bad,cutoff)
        with self.assertRaises(ValueError):deleted_sessions('unknown',web,cutoff)
        with self.assertRaises(ValueError):deleted_sessions(names[2],web,cutoff.replace(tzinfo=None))

    def test_both_actual_new_day_progress_contracts_and_unknown_changes(self):
        cut=datetime.datetime(2026,10,10,20,3,22,718197,tzinfo=datetime.timezone.utc)
        run='9f651096-aef9-4fba-90b0-a653e99f035a'
        old={k:[]for k in ['schubert.app_logs','schubert.request_inbox','schubert.log_cleanup_progress','schubert.inbox_inspection_progress']}
        common={'run_id':run,'cutoff':cut.isoformat(),'completed_at':(cut+datetime.timedelta(seconds=3)).isoformat()}
        log=dict(common,target_count=0,deleted_count=0,skipped_count=0,after_logged_at=None,after_id=None)
        inbox=dict(common,inspected_count=0,deleted_count=0,protected_count=0,after_message_id=None)
        new=dict(old);new['schubert.log_cleanup_progress']=[log];new['schubert.inbox_inspection_progress']=[inbox]
        self.assertEqual(len(zero_progress_post(old,new,cut,run,cut+datetime.timedelta(seconds=5))),2)
        for table,row in [('schubert.log_cleanup_progress',log),('schubert.inbox_inspection_progress',inbox)]:
            for k,v in [('run_id','foreign'),('cutoff',(cut-datetime.timedelta(microseconds=1)).isoformat()),('completed_at',None),('deleted_count',1),('extra',True)]:
                bad=dict(new);bad[table]=[dict(row,**{k:v})]
                with self.assertRaises(ValueError):zero_progress_post(old,bad,cut,run,cut+datetime.timedelta(seconds=5))
            bad=dict(new);bad[table]=[]
            with self.assertRaises(ValueError):zero_progress_post(old,bad,cut,run,cut+datetime.timedelta(seconds=5))
        bad=dict(old);bad['schubert.app_logs']=[{'logged_at':(cut-datetime.timedelta(hours=2160,microseconds=1)).isoformat()}]
        with self.assertRaises(ValueError):zero_progress_post(bad,new,cut,run,cut+datetime.timedelta(seconds=5))

if __name__ == '__main__':unittest.main()
