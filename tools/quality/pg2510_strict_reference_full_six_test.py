import subprocess
import unittest
from pg2510_strict_reference_full_six import SOURCE, server_source, validate
from pg2511_strict_reference_full_qualified import server


class FullCandidate(unittest.TestCase):
    def test_exact_source_and_fresh_full_count(self):
        validate(subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip())
        raw = server_source(SOURCE, 'a' * 64)
        for marker in ['PG2510', '3650', SOURCE]:
            self.assertIn(marker, raw)
        self.assertNotIn('PG2494-six-v1', raw)

    def test_independent_full_exact_count_and_physical_classes(self):
        raw = server()
        for marker in ["'batch':(1253,172,568)", '3650', SOURCE, "'semanticChangedClasses':6", 'MorningDatabaseSession$Session.class']:
            self.assertIn(marker, raw)
        self.assertIn("debug['verify'](a,bnew,1)", raw)
        self.assertIn("'sameSourceNativePending':True", raw)


if __name__ == '__main__':
    unittest.main()
