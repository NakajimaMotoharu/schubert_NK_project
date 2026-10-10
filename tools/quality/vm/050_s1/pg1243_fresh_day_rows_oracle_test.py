import datetime
import unittest
from pg1243_fresh_day_rows_oracle import deleted_sessions, session_post

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
        names=['schubert.auth_sessions','schubert.login_ip_attempts','schubert_web_session.web_http_sessions','schubert.batch_runs','schubert.app_logs','schubert_web_session.web_log_outbox','schubert.inbox_inspection_progress']+[f'schubert.fixture_{i}'for i in range(17)]
        old={name:[] for name in names};old[names[0]]=auth;old[names[2]]=web
        new=dict(old);new[names[0]]=auth[2:];new[names[2]]=web[2:]
        self.assertEqual(session_post(old,new,cutoff)['expectedSessionDeletes'],4)
        for table in names:
            bad=dict(new);bad[table]=[{'unexpected':True}]
            if table not in names[3:7]:
                with self.assertRaises((ValueError,KeyError)):session_post(old,bad,cutoff)
        for bad in [None,[None],[{'expires_at':None}]]:
            with self.assertRaises(ValueError):deleted_sessions(names[2],bad,cutoff)
        with self.assertRaises(ValueError):deleted_sessions('unknown',web,cutoff)
        with self.assertRaises(ValueError):deleted_sessions(names[2],web,cutoff.replace(tzinfo=None))

if __name__ == '__main__':unittest.main()
