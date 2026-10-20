import ast
import inspect
import unittest
import pg6214_original4027_artifacts as subject
from pg6042_original3976_artifacts import expected_case_keys


class Original(unittest.TestCase):
    def test_shared_reader_exact_finite_campaign_contract(self):
        import pg6042_original3976_artifacts as reader
        expected={('PG6040',(3976,593,1667),23),('PG6060',(3979,594,1667),1),
            ('PG6088',(3985,595,1667),5),('PG6118',(3988,595,1667),4),
            ('PG6196',(4024,605,1667),13),('PG6212',(4027,605,1667),7)}
        tree=ast.parse(inspect.getsource(reader.inspect_original));found=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Compare) and any(isinstance(op,ast.NotIn) for op in node.ops):
                right=node.comparators[-1]
                if isinstance(right,ast.Tuple):found.append(ast.literal_eval(right))
        self.assertIn(expected,[set(v) for v in found])
        self.assertIn(('PG6088','PG6118','PG6196','PG6212'),found)
        self.assertNotIn(('PG9999',(4027,605,1667),7),expected)
        # The transport boundary independently repeats the same finite export set.
        self.assertIn("data.get('campaign') not in ('PG6088', 'PG6118', 'PG6196', 'PG6212')",inspect.getsource(reader.collect))

    def test_three_actual_added_names_not_pass_arithmetic(self):
        rows=subject.new_case_identities(subject.original_source())
        self.assertEqual(3,len(expected_case_keys(rows)))
        self.assertEqual({'dev.codex.schubert.nk.api.file.ServiceResourceRetentionTest'},{r['class'] for r in rows})

    def test_pinned_new_whole_and_old_case_inputs(self):
        values=subject.definitions()['main'].__code__.co_consts
        for value in ('PG6212-six-v1','PG6196-current4024-cases/qualification.json',
            'PG6208-keeper-faults-qualification-v1/manifest.json','PG6212-current4027-cases',
            '4a89ed9b4c4f065c936b102a5740306be738ad8c55eef690e7c7484556a401d1',
            '50f54e2954bf8d8e248d7ec652fbb2e1920cd597ae9f71841161b5028eb99d7b'):
            self.assertIn(value,values)


if __name__=='__main__':unittest.main()
