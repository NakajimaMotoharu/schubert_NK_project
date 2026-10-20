import unittest
import pg6044_remaining33_static as t


class OriginalJarStaticProofTest(unittest.TestCase):
    def test_zero_literal_does_not_remove_other_rules(self):
        before = dict(AvoidLiteralsInIfCondition=33, AvoidCatchingGenericException=4)
        t.expected_rules(before, dict(AvoidCatchingGenericException=4))
        with self.assertRaises(ValueError):
            t.expected_rules(before, dict(AvoidCatchingGenericException=3))
        with self.assertRaises(ValueError):
            t.expected_rules(before, dict(AvoidLiteralsInIfCondition=1, AvoidCatchingGenericException=4))

    def test_full_physical_set_and_declared_owner(self):
        before = {str(i): 'a' for i in range(1666)} | {'batch:A.class': 'a'}
        after = dict(before) | {'batch:A.class': 'b'}
        self.assertEqual(['batch:A.class'], t.physical_changes(before, after, {'batch:A.class'}))
        with self.assertRaises(ValueError):
            t.physical_changes(before, dict(after) | {'0': 'changed'}, {'batch:A.class'})
        with self.assertRaises(ValueError):
            t.physical_changes(before, dict(after) | {'batch:B.class': 'added'}, {'batch:A.class'})


if __name__ == '__main__':
    unittest.main()
