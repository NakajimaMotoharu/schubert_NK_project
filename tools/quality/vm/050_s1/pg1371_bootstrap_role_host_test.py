"""Actual CP graph includes close assertion framework, full current fixture ABI."""
import ast
from pathlib import Path
import unittest
import pg1371_bootstrap_role_host_v2 as p

class Test(unittest.TestCase):
    def test_runtime_dependency_graph_and_new_only_slots(self):
        raw=p.source();ast.parse(raw)
        self.assertTrue("'runtimeLibraryHashes':libraries"in raw)
        self.assertFalse('pg1370-bootstrap-role-host-v1'in raw)
        self.assertTrue('PG1371-bootstrap-role-host-v2'in raw)
        self.assertEqual(4,len(p.LIBRARIES))
        repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
        for name in p.LIBRARIES:self.assertTrue((repo/name).is_file(),name)
        self.assertTrue("cp+=':'+':'.join(str(repo/name)for name in LIBRARIES)"in raw)
        self.assertTrue('sameOperatorHead'in raw and 'productionPtDelta'in raw)

if __name__=='__main__':unittest.main()
