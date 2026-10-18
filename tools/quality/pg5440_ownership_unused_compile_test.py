import ast
import unittest
from pyflakes.api import checkPath
import pg5440_ownership_unused_compile as entry


class HostCompiler(unittest.TestCase):
    def test_current_actual_abi_not_candidate_or_historical_old_jars(self):
        raw=entry.compiler();ast.parse(raw)
        for marker in('pg5430-candidate-build-v1.safe.json','pg5062-frozen-v1.safe.json','pg5060-current-owned-tools-v1',"old = W / 'pg4980-release-v1'",entry.role.view.SLOT):
            self.assertIn(marker,raw)
        for marker in('pg4918-frozen-v1','pg4860-release-v1','pg4980-candidate-build-v1.safe.json'):
            self.assertNotIn(marker,raw)
        for path in(entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
