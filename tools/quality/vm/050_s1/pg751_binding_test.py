"""Literal actual current737/currentPG715 binding and private preservation; no VM operation."""
import ast
import unittest
from pg751_current_baseline import source


class Test(unittest.TestCase):
    def test_actual_actor_private_roots_current_signature_and_readonly_post(self):
        raw=source();ast.parse(raw)
        for v in ('pg751-completed-baseline-v1','pg737-bootstrap-existing-v1/after.private.json',
            '25e00f13202b08b8db34a8c95b77933ff44cd71d5c37de0fa3cc9aacd5c0609e',
            '2793207','13042489','0d42d02df3a44b7bb036140f6cc076cf','2aff8ecf3b7d4d15b24a8af0f73a8745',
            '0.1.0-PG715','1ec19782a1afe22d1de75b05f4cd12b8a8a8a172',
            '74d35361865a32a6b992f93d78d42844e20a5bb286fa4fc4b5e74520fa6305d5',
            'pg738-bootstrap-final-v1.exit',"'batchRows':534"):
            self.assertIn(v,raw)
        for group in ('664','702','737'):
            for kind in ('tools','verify','existing'):
                self.assertIn('pg'+group+'-bootstrap-'+kind+'-v1',raw)
        self.assertNotIn('2464638',raw)
        self.assertNotIn('d420de6553ef48038a40332c37a8b12e',raw)
        self.assertIn('current_gc_after_known20',raw)
        self.assertIn('configuration_after_gc',raw)


if __name__=='__main__':unittest.main()
