import ast
import inspect
import unittest
import pg6332_original4048_artifacts as subject
from pg6042_original3976_artifacts import expected_case_keys
from pyflakes.api import checkPath


class Definition(unittest.TestCase):
    def test_five_real_new_methods_four_classes_not_success_arithmetic(self):
        rows=subject.new_case_identities('aed19c6dca368e9717309d6f744d7917c6b7b32c')
        self.assertEqual(5,len(expected_case_keys(rows)));self.assertEqual(4,len({r['class']for r in rows}))
        self.assertEqual({'api','web'},{r['module']for r in rows})

    def test_finite_profile_and_original_source_qualification_only(self):
        import pg6042_original3976_artifacts as reader
        tree=ast.parse(inspect.getsource(reader.inspect_original));found=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Compare)and any(isinstance(op,ast.NotIn)for op in node.ops):
                right=node.comparators[-1]
                if isinstance(right,ast.Tuple):found.append(ast.literal_eval(right))
        self.assertTrue(any(('PG6330',(4048,607,1667),4)in item for item in found))
        self.assertIn(('PG6088','PG6118','PG6196','PG6212','PG6244','PG6272','PG6302','PG6330', 'PG6386', 'PG6408', 'PG6452', 'PG6490'),found)
        values=subject.definitions()['main'].__code__.co_consts
        for item in ('PG6330-six-v1','PG6302-current4043-cases/qualification.json',
            'PG6326-web-graph-qualification-v1/manifest.json','PG6330-current4048-cases',
            'eed16f1405f305011467e1a0154747ae0c3483bb0d37e98888a2f9f2816b79a1',
            '9ebb095baca6637058bcf3361c8b71428405827f6deb464f69ad65269cfee770'):
            self.assertIn(item,values)
        for path in (subject.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
