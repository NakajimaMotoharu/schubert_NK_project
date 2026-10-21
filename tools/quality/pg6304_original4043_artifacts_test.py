import ast
import inspect
import unittest
import pg6304_original4043_artifacts as subject
from pg6042_original3976_artifacts import expected_case_keys


class Definition(unittest.TestCase):
    def test_three_real_new_methods_not_success_arithmetic(self):
        rows=subject.new_case_identities('5eb040421ae9ea06ecc70c6eb2e152871c2d0d42')
        self.assertEqual(3,len(expected_case_keys(rows)))
        self.assertEqual({'dev.codex.schubert.nk.web.messaging.ArtemisRequestSenderTest','dev.codex.schubert.nk.web.logging.WebLogMessageSenderTest'},{r['class']for r in rows})

    def test_explicit_finite_profile_and_original_bindings(self):
        import pg6042_original3976_artifacts as reader
        tree=ast.parse(inspect.getsource(reader.inspect_original));found=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Compare)and any(isinstance(op,ast.NotIn)for op in node.ops):
                right=node.comparators[-1]
                if isinstance(right,ast.Tuple):found.append(ast.literal_eval(right))
        self.assertTrue(any(('PG6302',(4043,607,1667),2)in item for item in found))
        self.assertIn(('PG6088','PG6118','PG6196','PG6212','PG6244','PG6272','PG6302','PG6330', 'PG6386', 'PG6408', 'PG6452', 'PG6490'),found)
        values=subject.definitions()['main'].__code__.co_consts
        for item in ('PG6302-six-v1','PG6272-current4040-cases/qualification.json',
            'PG6298-web-send-qualification-v1/manifest.json','PG6302-current4043-cases',
            'dc3e2e9b2cb435307b3c248964452e93dfc008a23a69072d8d4e9046dec8eed5',
            '976a384def5907769df7cee4ea2848bc5f29aad3a9504a35bf7cde30a1fb4ae7'):
            self.assertIn(item,values)


if __name__=='__main__':unittest.main()
