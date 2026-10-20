"""Pre-issue generation controls; no host authentication/job or runtime operation."""
import ast
import unittest
from pyflakes.api import check
import pg5780_jms_primary_whole as p


class Whole3939Plan(unittest.TestCase):
    def test_standalone_same_source_and_exact_inventory(self):
        raw=p.server_source(p.SOURCE,'0'*64);values=[n.value for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Constant)and type(n.value)is int]
        self.assertIn(3939,values);self.assertIn(583,values);self.assertIn(1664,values)
        self.assertNotIn(3932,values);self.assertNotIn(581,values)
        self.assertEqual(0,check(raw,'whole3939-complete'));self.assertNotIn('systemctl',raw)

    def test_new_only_source_paths_and_old_job_not_replayed(self):
        raw=p.driver_source({'host':'PREFLIGHT_NOT_RUN','matchingActiveJobs':[]})
        self.assertIn("'tests': 3939, 'suites': 583, 'mainClasses': 1664",raw)
        self.assertIn('pg5780-jms-primary-six-v1',raw);self.assertIn('pg5780-full.py',raw)
        self.assertIn('BUG1485 three same-identity',raw);self.assertTrue(callable(p.RUNTIME.preflight))
        self.assertTrue(callable(p.RUNTIME.previous.driver.main))


if __name__=='__main__':unittest.main()
