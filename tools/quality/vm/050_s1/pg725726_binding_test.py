"""No actual authority: fixed current PID1/source/preservation and delegation oracle."""
import unittest
import pg725_capture_done as p
import pg726_a01_current as a


class BindingTest(unittest.TestCase):
    def test_actual_current_tuple_and_unchanged_budget(self):
        raw=p.payload('11111111-2222-4333-8444-555555555555');compile(raw,'<new current DONE>', 'exec')
        for text in ('2468821','2aff8ecf3b7d4d15b24a8af0f73a8745','132812','127549297774',
                     '96a45c46a3e3f33924331fdebfb716bf1a47581b9eb3765f1a00eb4a8d09514e',
                     '1ec19782a1afe22d1de75b05f4cd12b8a8a8a172','PG715','pg722-fresh-parent-v1','pg725-completed-readonly-v1'):
            self.assertIn(text,raw)
        for old in ('2146618','122726','pg690','PG682'):
            self.assertNotIn(old,raw)
        with self.assertRaises(AssertionError):p.payload('8633b77f-77dc-4a78-88b4-41165f159b43')

    def test_current_driver_not_baseline_mutation(self):
        raw=a.code();compile(raw,'<Current driver>', 'exec')
        for text in ('pg724-retention-post-v1.exit','pg723-observer-v1','PG726-native-a01-v1','PG715',
                     '1ec19782a1afe22d1de75b05f4cd12b8a8a8a172'):
            self.assertIn(text,raw)
        self.assertIn('Current',raw)
        for old in ('pg690','pg691','pg692','PG694'):
            self.assertNotIn(old,raw)


if __name__=='__main__':unittest.main()
