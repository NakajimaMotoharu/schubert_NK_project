import datetime
import unittest
from pg1462_current_day_inspector import payload,EXPECTED_OUTBOX


class InspectorOracleTest(unittest.TestCase):
    def test_exact_retention_boundaries_independently(self):
        cut=datetime.datetime(2026,10,11,21,18,59,tzinfo=datetime.timezone.utc)
        body=EXPECTED_OUTBOX[:EXPECTED_OUTBOX.index('outbox_count=')]
        def require(value):
            if not value:raise ValueError('aware times required')
        ns={'datetime':datetime,'cut':cut,'require':require};exec(body,ns)
        fixture={'status':'SENT','sent_at':(cut-datetime.timedelta(hours=168,seconds=1)).isoformat(),'lease_until':None}
        self.assertTrue(ns['expired_outbox'](fixture))
        for changed in [dict(fixture,status='NEW'),dict(fixture,sent_at=None),dict(fixture,sent_at=(cut-datetime.timedelta(hours=168)).isoformat()),dict(fixture,lease_until=cut.isoformat())]:self.assertFalse(ns['expired_outbox'](changed))
        self.assertTrue(ns['expired_outbox'](dict(fixture,lease_until=(cut-datetime.timedelta(microseconds=1)).isoformat())))

    def test_current_actual_scope_no_old_native_expected(self):
        s=payload();compile(s,'<actual Inspector proof>','exec')
        self.assertIn('15700a87-9117-4f63-a0ff-768dd604d0f1',s)
        self.assertIn('2026-10-12',s)
        self.assertIn('outbox_count if k',s)
        self.assertNotIn('17228',s)
        self.assertNotIn('d5b0010',s)
        self.assertIn("'nativeCounterAccepted':False",s)


if __name__=='__main__':unittest.main()
