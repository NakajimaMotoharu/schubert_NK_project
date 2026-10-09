"""Current cohort genuine receipt and unchanged driver route, no VM action."""
import unittest
from unittest.mock import patch
from pg693_capture_done import payload
from pg694_a01_current import code
from pg694_a01_current import main as driver_main


class BindingTest(unittest.TestCase):
    def test_driver_entry_delegates_and_preserves_failure(self):
        with patch('pg694_a01_current.code',return_value='def main():\n return None\n'):
            self.assertIsNone(driver_main())
        with patch('pg694_a01_current.code',return_value="def main():\n raise ValueError('independent entry sentinel')\n"):
            with self.assertRaisesRegex(ValueError,'independent entry sentinel'):driver_main()

    def test_new_done_not_prior_completed_campaign(self):
        raw=payload('aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee');compile(raw,'<genuine new>','exec')
        for text in ('119288459330','2146618','122726','6b3dd954959c43c1bbac2164ec9d0c6b',
                     'pg693-completed-readonly-v1','pg690-fresh-parent-v1','c2a125086080538d44a434dd3313999d45d075a7debab2f103e984908707d982',
                     'ownedUnits','parentEndedUTC',"env['completed'](pid1,done)",'manager.UnrefUnit(u)','bus.close()',
                     '9bd50536f692610036a0ed8b83e0a8b35fe2a66f'):
            self.assertIn(text,raw)
        for old in ('e49243d5-de84-4714-8612-6912ddc17e9e','3a53b979-fa01-47dd-92a6-7b26affcfb5c','601297d0-a8ba-47da-852b-0ffeae409965','aaaaaaaa-bbbb-1ccc-8ddd-eeeeeeeeeeee'):
            with self.subTest(old=old),self.assertRaises(AssertionError):payload(old)

    def test_current_driver_no_baseline_mutation_and_fixed_generation(self):
        raw=code();compile(raw,'<A01 new>','exec')
        for text in ('pg690-start-v1','pg691-watch-private-v1','pg692-retention-post-v1.exit','PG694-native-a01-v1',
                     '122dcc4c1be482ac3239325de6fb3d4bec12747d05adce3929c319ab5bdfd71d',
                     'NativeNkA01Capture','baseline_sha','1800000000','sameCapturedParentApiWebCaddyBeforeAfter'):
            self.assertIn(text,raw)
        for old in ('PG631','pg650','pg651','PG654','daemon-reload',"['systemctl','start'","['systemctl','stop'"):
            self.assertNotIn(old,raw)


if __name__=='__main__':unittest.main()
