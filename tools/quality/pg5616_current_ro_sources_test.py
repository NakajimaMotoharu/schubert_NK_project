import unittest
from pyflakes.api import check,checkPath
import pg5616_current_ro_sources as role


class CurrentReadOnlyRoles(unittest.TestCase):
    def test_all18_static_after_actual_unused_post_and_distinct_roles(self):
        r=role.qualify();self.assertEqual(r['nativePhysicalFiles'],94)
        values=role.sources();self.assertEqual(len(values),18)
        self.assertIn('Pg5616CandidateRo.java',values)
        for name,raw in values.items():
            if name.endswith('.py'):self.assertEqual(check(raw,name),0)
        self.assertNotEqual(role.CURRENT,role.SOURCE);self.assertEqual(role.unused.BEFORE,role.BEFORE)
        for path in(role.__file__,__file__):self.assertEqual(checkPath(path),0)

    def test_wrong_candidate_or_before_cannot_change_factory_profile(self):
        for bom,before in(('0'*64,role.BEFORE),(role.BOM,'0'*64)):
            with self.assertRaises(ValueError):role.sources(bom,before)


if __name__=='__main__':unittest.main()
