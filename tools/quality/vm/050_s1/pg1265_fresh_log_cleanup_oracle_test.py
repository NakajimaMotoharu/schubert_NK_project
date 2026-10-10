import copy
import unittest
from pg564_log_session_oracle_test import Test as Vectors
from pg1265_fresh_log_cleanup_oracle import verify_fresh


class FreshCleanupLogTest(unittest.TestCase):
    def setUp(self):
        self.v = Vectors(); self.v.setUp()
        self.old = copy.deepcopy(self.v.old)
        self.expired = dict(self.v.session, id='00000000-0000-4000-8000-000000000004', expires_at='2026-10-08T04:25:00.123000Z')
        self.retained = dict(self.v.session, id='00000000-0000-4000-8000-000000000005')
        self.old['schubert_web_session.web_http_sessions'] = [self.expired, self.retained]
        self.current = copy.deepcopy(self.v.new)
        self.current['schubert_web_session.web_http_sessions'].append(self.retained)

    def run_oracle(self, old=None, current=None, events=None, count=1):
        return verify_fresh(self.old if old is None else old, self.current if current is None else current,
                            [self.v.local] if events is None else events, self.v.key, self.v.session_key,
                            self.v.when, count)

    def test_boundary_expiry_retention_and_independent_wire_crypto(self):
        value = self.run_oracle()
        self.assertEqual(value['independentExpiredSessionCount'], 1)
        self.assertEqual(value['priorRetainedSessionCount'], 1)
        self.assertEqual(value['logWireDbLocalVerified'], 1)
        self.assertFalse(value['externalFixtureRequestCountKnown'])
        self.assertFalse(value['qa051FinalPass'])
        self.assertEqual(self.old['schubert_web_session.web_http_sessions'], [self.expired, self.retained])
        self.assertEqual(len(self.current['schubert_web_session.web_http_sessions']), 2)

    def test_recreated_mutated_duplicate_missing_null_and_causal_failures(self):
        table = 'schubert_web_session.web_http_sessions'
        for rows in ([self.v.session, self.retained, self.expired], [self.v.session],
                     [self.v.session, dict(self.retained, version=99)],
                     [self.v.session, self.retained, self.retained]):
            bad = copy.deepcopy(self.current); bad[table] = rows
            with self.assertRaises(ValueError): self.run_oracle(current=bad)
        for old, current, events, count in [(None, self.current, [], 1), (self.old, None, [], 1),
                                          (self.old, self.current, None, 1), (self.old, self.current, [], True),
                                          (self.old, self.current, [], 0)]:
            with self.assertRaises(ValueError): verify_fresh(old, current, events, self.v.key, self.v.session_key, self.v.when, count)
        for events in ([], [self.v.local, self.v.local], [dict(self.v.local, status=404)]):
            with self.assertRaises(ValueError): self.run_oracle(events=events)
        bad = copy.deepcopy(self.current); bad['schubert_web_session.web_log_outbox'][0]['status'] = 'ERROR'
        with self.assertRaises(ValueError): self.run_oracle(current=bad)


if __name__ == '__main__': unittest.main()
