"""Independent literal captured Root/schema oracle; no Production calls."""
import copy
import unittest
from pg1700_new_source_live_binding import captured_parent


class CaptureTest(unittest.TestCase):
    def test_actual_and_rejected_envelopes(self):
        expected = {'MainPID': '302199', 'InvocationID': 'fe43e94b1fbf4886bb4ab3922fd16f9c',
                    'Job': '106924', 'ExecMainStartTimestampMonotonic': '66941284515'}
        start = {'actualExit': 0, 'payloadSha256': 'e38ba715fc03defe5f67b4032df33e73cf8641afeea88bbdc5ea2bca97020805',
                 'guest': {**expected, 'clientExit': 0, 'ordinaryNoargs': True, 'originalBudgetSeconds': 1800}}
        before = {'actualExit': 0, 'productionSource': '2741c4546afad6c1e8b6efbd53dfb58144edf7bb',
                  'whole187SignedArtifactBytesVerified': True, 'newSourceParentNotStarted': True}
        self.assertEqual(expected, captured_parent(start, before))
        for key in expected:
            bad = copy.deepcopy(start); bad['guest'][key] = 'foreign'
            with self.subTest(key=key), self.assertRaises(ValueError): captured_parent(bad, before)
        for key in ('guest', 'payloadSha256', 'actualExit'):
            bad = copy.deepcopy(start); bad.pop(key)
            with self.subTest(missing=key), self.assertRaises(ValueError): captured_parent(bad, before)
        for bad in (None, {}, {'actualExit': 0, 'parent': expected, 'productionSource': before['productionSource']}):
            with self.subTest(schema=bad), self.assertRaises(ValueError): captured_parent(bad, before)
        for key, value in [('productionSource','4d6bcbddb417b76d27e52d5d9640752c300edccf'),
                           ('actualExit',1),('whole187SignedArtifactBytesVerified',False),('newSourceParentNotStarted',None)]:
            bad = dict(before); bad[key] = value
            with self.subTest(before=key), self.assertRaises(ValueError): captured_parent(start, bad)


if __name__ == '__main__': unittest.main()
