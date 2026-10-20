"""Unknown body, changed primary, swallowed/wrapped failures are never reviewed by shape."""
import unittest
from pg5772_primary_capture_review import retained_body


class ExactCapture(unittest.TestCase):
    def test_same_capture_and_same_throw_only(self):
        self.assertEqual(1,retained_body(') { primary=failure; throw failure; } finally {',0,'RuntimeException failure','primary')[0])
        for s in(') { primary=null; throw failure; } finally {',') { primary=failure; return; } finally {',') { primary=failure; throw new Error(failure); } finally {',') { other=failure; throw failure; } finally {',') { primary=failure; audit(); throw failure; } finally {',') { primary=failure; throw failure; }'):
            with self.assertRaisesRegex(ValueError,'two-statement'):retained_body(s,0,'RuntimeException failure','primary')


if __name__=='__main__':unittest.main()
