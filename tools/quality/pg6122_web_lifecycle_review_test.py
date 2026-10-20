"""Definition checks; no Production or fixture job invocation."""
import inspect
import unittest
from collections import Counter
from pyflakes.api import check
import pg6122_web_lifecycle_review as subject


class Definition(unittest.TestCase):
    def test_exact_ten_explicit_nonblank_individual_sites(self):
        self.assertEqual(10, len(subject.SITES))
        self.assertEqual(Counter(WebHttpAdmission=6, WebLogReplayWorker=2, RevocationRetryWorker=1, WebRequestTrace=1), Counter(k[0] for k in subject.SITES))
        self.assertTrue(all(len(v) > 80 for v in subject.SITES.values()))
        self.assertEqual(4, len(subject.CLASSES))

    def test_definition_is_static_and_explicit(self):
        source = inspect.getsource(subject)
        self.assertEqual(0, check(source, '<lifecycle review definition>'))
        self.assertNotIn('subprocess.run', source)
        self.assertIn('javap', source)
        self.assertIn('currentWholeJoinPending=True', source)
        self.assertIn('newPtPassesClaimed=0', source)


if __name__ == '__main__':
    unittest.main()
