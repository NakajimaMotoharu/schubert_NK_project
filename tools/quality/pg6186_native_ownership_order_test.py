import unittest
import pg6186_native_ownership_order as subject


class Definition(unittest.TestCase):
    def test_java_tokens_preserve_literals_and_ignore_comments_only(self):
        self.assertEqual(subject.tokens('f ( "a b" ); // ignored'),subject.tokens('f("a b");'))
        self.assertNotEqual(subject.tokens('f("a b");'),subject.tokens('f("ab");'))
        self.assertNotEqual(subject.tokens('f("QSBREQ01");'),subject.tokens('f("QSSREQ01");'))

    def test_owned_release_true_is_not_a_false_flag_or_missing_scope(self):
        body='''       0: iconst_1
       1: invokestatic #1 // Method ServiceProcessResources.ownedRelease:()V
       4: invokestatic #2 // Method ResourceScope.acquire:()V
       7: return
'''
        self.assertEqual([('fixture',1,1)],subject.true_release_ports({'fixture':body},1))
        with self.assertRaises(ValueError):subject.true_release_ports({'fixture':body.replace('iconst_1','iconst_0')},1)
        with self.assertRaises(ValueError):subject.true_release_ports({'fixture':body.replace('ResourceScope.acquire:','Other.scope:')},1)

    def test_call_counter_requires_exact_actual_method_reference(self):
        body='''       0: invokestatic #3 // Method Some.nativeEntry:()V
       3: return
'''
        self.assertEqual([('fixture',0,0)],subject.one_call({'fixture':body},'Some.nativeEntry:'))
        with self.assertRaises(ValueError):subject.one_call({'fixture':body},'Some.oldEntry:')


if __name__=='__main__':unittest.main()
