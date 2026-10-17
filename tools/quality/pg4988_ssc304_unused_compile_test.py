"""Current ABI/candidate placement graph preparation; management tests only."""
import ast
import unittest
from pyflakes.api import checkPath
import pg4988_ssc304_unused_compile as role
import pg4990_ssc304_unused_dispatch as dispatch


class Compiler(unittest.TestCase):
    def test_current_abi_and_exact_independent_phase_markers(self):
        raw=role.compiler();ast.parse(raw)
        for marker in('pg4980-candidate-build-v1.safe.json','pg4980-release-v1','pg4980-manifest-v1.sig',
            role.role.view.SLOT,'pg4918-frozen-v1.safe.json','pg4916-current-owned-tools-v1',
            "old = W / 'pg4860-release-v1'",'Pg4986NativeArgumentTest','Pg4986OriginalTupleTest',
            'Pg4986CurrentIdentityTest','Pg4986InputBoundaryTest',"'-Xlint:all', '-Werror'","'argument'","'label'"):
            self.assertIn(marker,raw)
        for bad in('pg4774','pg4772','pg4706','systemctl','daemon-reload'):self.assertNotIn(bad,raw)
        for p in(role.__file__,dispatch.__file__,__file__):self.assertEqual(0,checkPath(p))

    def test_current_history_not_manager_gc_permission_and_scope_stays_readonly(self):
        before=dispatch.before_record();_,normal,_=role.role.current_tuple()
        self.assertEqual(normal,before['genuineCompletion']);self.assertTrue(before['dataOnlyNotRuntimeAuthority'])
        self.assertEqual(80,before['nativePhysicalFiles']);self.assertFalse(before['nativeCandidateCredit'])
        self.assertTrue(before['runtimeAlreadyRetired']);self.assertTrue(before['allTenUnitsKernelEmpty'])
        self.assertIn("require(not os.path.lexists('/var/lib/schubert-nk/maintenance/active'))",role.role.view.payload())
        self.assertIn("glob('*.start.intent')",role.role.view.payload())
        self.assertNotIn('management_gate',dispatch.source());ast.parse(dispatch.stage_source());ast.parse(dispatch.source())


if __name__=='__main__':unittest.main()
