"""PT-OPS-PG553-P003: independent literal cutoff window, no private inputs."""
import copy
import unittest
from pg553_inbox_oracle import bounded_candidates

TABLES=['schubert.'+t for t in ['notifications','questions','auth_sessions','login_ip_attempts','mq_outbox','app_logs','batch_runs','inbox_inspection_progress','log_cleanup_progress','request_inbox']]+['schubert_web_session.'+t for t in ['web_http_sessions','web_log_outbox','web_receipt_references']]


class Test(unittest.TestCase):
    def test_literal_web_window_auth_ip_and_protected(self):
        rows={t:[]for t in TABLES}
        rows['schubert_web_session.web_http_sessions']=[{'id':n,'expires_at':t}for n,t in [('old','2026-10-08T02:59:59Z'),('low','2026-10-08T03:00:00Z'),('mid','2026-10-08T03:15:00Z'),('high','2026-10-08T03:30:00Z'),('future','2026-10-08T03:30:00.000001Z')]]
        rows['schubert.login_ip_attempts']=[{'client_address':'literal','window_started_at':'2026-10-07T02:44:59Z','locked_until':None}]
        bounds={'lower':'2026-10-08T03:00:00Z','upper':'2026-10-08T03:30:00Z'}
        lo,mid,hi=bounded_candidates(rows,bounds,'2026-10-08T03:15:00Z')
        self.assertEqual(lo['web_http_sessions'],['low','old'])
        self.assertEqual(mid['web_http_sessions'],['low','mid','old'])
        self.assertEqual(hi['web_http_sessions'],['high','low','mid','old'])
        self.assertEqual(mid['login_ip_attempts'],['literal'])
        for bad in ['2026-10-08T02:59:59.999999Z','2026-10-08T03:30:00.000001Z',None,'bad']:
            with self.assertRaises((ValueError,TypeError)):bounded_candidates(rows,bounds,bad)
        changed=copy.deepcopy(rows);changed['schubert.auth_sessions']=[{'id':'changes','expires_at':'2026-10-07T03:15:00Z','revoked':False,'revoked_at':None}]
        with self.assertRaises(ValueError):bounded_candidates(changed,bounds,bounds['lower'])


if __name__=='__main__':unittest.main()
