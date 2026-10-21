import ast
import inspect
import unittest
import pg6274_original4040_artifacts as subject
from pg6042_original3976_artifacts import expected_case_keys


class Definition(unittest.TestCase):
    def test_six_actual_new_methods_not_success_arithmetic(self):
        source='b4230118efcc429ee29d6e6f5761c55175f1e85e'
        rows=subject.new_case_identities(source)
        self.assertEqual(6,len(expected_case_keys(rows)))
        self.assertEqual({'dev.codex.schubert.nk.api.messaging.outbound.OutboxFailureOwnershipTest'},{r['class']for r in rows})

    def test_explicit_finite_campaign_and_current_reader_bindings(self):
        import pg6042_original3976_artifacts as reader
        tree=ast.parse(inspect.getsource(reader.inspect_original));found=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Compare)and any(isinstance(op,ast.NotIn)for op in node.ops):
                right=node.comparators[-1]
                if isinstance(right,ast.Tuple):found.append(ast.literal_eval(right))
        self.assertTrue(any(('PG6272',(4040,607,1667),2)in item for item in found))
        self.assertIn(('PG6088','PG6118','PG6196','PG6212','PG6244','PG6272','PG6302'),found)
        values=subject.definitions()['main'].__code__.co_consts
        for item in ('PG6272-six-v1','PG6244-current4034-cases/qualification.json',
            'PG6268-outbox-failure-qualification-v1/manifest.json','PG6272-current4040-cases',
            '129f400938285f04cb016292b8e0822835f22d67bf3f899ec2f6e6b7b23004e9',
            '1f54f48b8ffd26d9739e74a0aa80ef4296c95a6096edb145783b274c44d638a8'):
            self.assertIn(item,values)


if __name__=='__main__':unittest.main()
