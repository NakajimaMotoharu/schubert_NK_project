import ast
import json
import unittest
from pyflakes.api import checkPath
import pg5442_ownership_unused_dispatch as entry


class Dispatch(unittest.TestCase):
    def test_exact_fresh88_and_normal_history_only(self):
        before=entry.before_record()
        self.assertTrue(before['dataOnlyNotRuntimeAuthority'])
        self.assertTrue(before['runtimeAlreadyRetired'])
        self.assertTrue(before['allClientAdvisoryFlock0'])
        self.assertTrue(before['allTenUnitsKernelEmpty'])
        candidate=json.loads((entry.role.W/'pg5430-candidate-build-v1.safe.json').read_bytes())
        ns=entry.runtime_namespace(candidate,before)
        self.assertEqual(ns['SOURCE'],entry.role.SOURCE)
        self.assertEqual(ns['BASELINE_SHA'],entry.role.BEFORE)
        for raw in(entry.source(),entry.stage_source()):ast.parse(raw)
        raw=entry.source()
        for marker in('pg5442-stage-v1.exit','pg5440-frozen-v1.safe.json','pg5430-manifest-v1.sig','0.1.0-PG5430','0.1.0-PG4980',entry.role.SOURCE):self.assertIn(marker,raw)
        self.assertNotIn('0.1.0-PG4860',raw)
        for path in(entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
