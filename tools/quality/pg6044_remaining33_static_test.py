import unittest
import pg6044_remaining33_static as t


class OriginalJarStaticProofTest(unittest.TestCase):
    def test_only_numeric_cp_and_comment_alignment_are_normalized(self):
        original = '  void value();\n    descriptor: ()V\n    Code:\n       0: ldc           #99                  // String one  two\n       2: invokedynamic #7, 0 // InvokeDynamic #0:call:()V\n       7: return\n}'
        equivalent = original.replace('#99                  //', '#100                 //')
        self.assertEqual(t.executable_sections(original), t.executable_sections(equivalent))
        for old, new in [('ldc ', 'ldc_w '), ('()V', '()I'), ('one  two', 'one two'), ('String one  two', 'String different'), ('InvokeDynamic #0:', 'InvokeDynamic #1:')]:
            self.assertNotEqual(t.executable_sections(original), t.executable_sections(equivalent.replace(old, new)))

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
