"""No writer call or invented timestamp; original durable phase and current inode unchanged."""
import unittest
from pyflakes.api import check
from pg2006_existing_runtime_independent_post import payload


class Post(unittest.TestCase):
    def test_actual_independent_existing_file_bound_and_all_resources(self):
        raw=payload();self.assertEqual(0,check(raw,'<actual whole independent post>'))
        self.assertTrue('pg1995-partial-runtime-recovery-full-post-v1/before.private.json' in raw)
        self.assertTrue('pg1984-fresh-resume-preparation-v1/before.private.json' in raw)
        self.assertTrue('existingFileNoRewrite' in raw);self.assertTrue('old1983CloseUnknownRetained' in raw)
        self.assertTrue('runtime_actual==json.loads(pending_raw)' in raw)
        for forbidden in ['fixed_dropin(','resume_contract.','mutation_begin_ns','runtime-prepared.private.json']:
            self.assertTrue(forbidden not in raw,'no producer or missing phase '+forbidden)
        self.assertTrue("lines[-2:] == [b'0', b'0']" in raw)


if __name__=='__main__':unittest.main()
