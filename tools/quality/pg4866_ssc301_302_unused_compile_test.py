import ast
import unittest
from pyflakes.api import checkPath
import pg4866_ssc301_302_unused_compile as role


class Compiler(unittest.TestCase):
    def test_actual_current_not_candidate_abi_and_all_independent_phases(self):
        raw=role.compiler();ast.parse(raw)
        for marker in ['pg4860-candidate-build-v1.safe.json','pg4860-release-v1','pg4860-manifest-v1.sig',role.role.view.SLOT,'pg4774-frozen-v1.safe.json','pg4772-new-current-owned-tools-v1',"old = W / 'pg4702-release-v1'",'Pg4864NativeArgumentTest','Pg4864OriginalTupleTest','Pg4864CurrentIdentityTest','Pg4864InputBoundaryTest',"'-Xlint:all', '-Werror'","'argument'","'label'"]:
            self.assertIn(marker,raw)
        for bad in ('pg4654','pg4652','pg4706','pg4432','systemctl','daemon-reload'):
            self.assertNotIn(bad,raw)
        self.assertEqual(0,checkPath(role.__file__));self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
