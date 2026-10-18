import unittest
import pg5158_native_coverage_bytecode as role
import pg5122_root_elf_public as public


class DeltaProof(unittest.TestCase):
    def test_expanded_publication_module_map_accepts_same_owner_only(self):
        self.assertEqual(public.suite_map({'A':'bootstrap'},{'A':'bootstrap','B':'storage'}),
                         {'A':'bootstrap','B':'storage'})
        for extra in ({'A':'batch'},{'B':'unknown'}):
            with self.assertRaises(ValueError):public.suite_map({'A':'bootstrap'},extra)

    def test_only_declared_target_can_change_and_all_other_members_are_bound(self):
        before={role.KEY:'old','other':'fixed'}
        role.require_only_target_delta(before,{role.KEY:'new','other':'fixed'})
        for after in (before,{role.KEY:'new','other':'foreign'},
                      {role.KEY:'new'},{role.KEY:'new','other':'fixed','extra':'x'}):
            with self.assertRaises(ValueError):role.require_only_target_delta(before,after)


if __name__=='__main__':unittest.main()
