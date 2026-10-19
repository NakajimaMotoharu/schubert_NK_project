import inspect
import unittest
from pyflakes.api import check,checkPath
import pg5588_scope_canary_whole as entry


class CorrectedWhole(unittest.TestCase):
    def test_actual3905_standalone_keeps563_all1664_format_first(self):
        raw=entry.server_source(entry.SOURCE,'a'*64)
        self.assertEqual(check(raw,'<new3905 complete>'),0)
        self.assertIn('PG5588',raw);self.assertNotIn('PG5572',raw)
        self.assertIn('3905',raw);self.assertIn('563',raw);self.assertIn('1664',raw);self.assertIn('format-before-pt',raw)

    def test_fresh_driver_and_source_same_input_and_failure_preservation_guards(self):
        raw=entry.driver_source({'matchingActiveJobs':[]})
        scope={**vars(entry.previous.previous.previous.driver),'SOURCE':entry.SOURCE,'LABEL':entry.LABEL,'server_source':entry.server_source}
        exec(compile(raw,'<new-only driver namespace>','exec'),scope)
        self.assertTrue(callable(scope['main']));self.assertIn("'tests': 3905",raw)
        guard=inspect.getsource(entry.prerequisites)
        self.assertIn("failed['actualExit']==1",guard);self.assertIn("green['actualCases']==73",guard)
        self.assertIn('only documented scope oracle',guard)
        for path in(entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
