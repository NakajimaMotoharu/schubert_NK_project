import unittest
import pg6748_owned_reader_whole as p
import pg6750_original4189_owned_artifacts as original


class GroupedOwnedWholeDefinitionTest(unittest.TestCase):
    def test_all_current_declarations_not_old_pass_arithmetic(self):
        self.assertEqual((4189,645),p.declared_inventory())
        cases=original.added_cases('HEAD')
        self.assertEqual(5,len(cases));self.assertEqual({'bootstrap','batch'},{r['module']for r in cases})

    def test_server_source_is_same_bounded_profile_with_exact_new_inventory(self):
        raw=p.server_source('0'*40,'0'*64)
        self.assertIn('4189',raw);self.assertIn('645',raw)
        self.assertNotIn('systemctl',raw);self.assertNotIn('qemu-system',raw)

    def test_original_physical_zero_change_rejects_any_changed_class(self):
        changed,added,same=original.unchanged_physical({'x.class':'a'},{'x.class':'a'},set(),(1,1),[])
        self.assertEqual(([],[],1),(changed,added,same))
        for after,counts in (({'x.class':'b'},(1,1)),({'x.class':'a','y.class':'b'},(1,2)),({},(1,0)),({'x.class':'a'},(2,2))):
            with self.assertRaises(ValueError):original.unchanged_physical({'x.class':'a'},after,set(),counts,[])
        with self.assertRaises(ValueError):original.unchanged_physical({'x.class':'a'},{'x.class':'a'},set(),(1,1),None)

    def test_old_nonempty_owner_guard_and_emitted_namespace_remain_strict(self):
        self.assertEqual((['x.class'],[],0),original.unchanged_physical({'x.class':'a'},{'x.class':'b'},{'x.class'},(1,1),[]))
        with self.assertRaises(ValueError):original.unchanged_physical({'x.class':'a'},{'x.class':'a'},{'x.class'},(1,1),[])
        raw=original.emitted('0'*64,'/home/mini/schubert-nk-pgpt/transfer/PG6750-original4189-owned-v1')
        self.assertIn("('PG6748', (4189, 645, 1667), 0)",raw)
        self.assertIn('or not owners or not owners <= changed',raw)
        self.assertIn('changed, added, unchanged = unchanged_physical(',raw)


if __name__=='__main__':unittest.main()
