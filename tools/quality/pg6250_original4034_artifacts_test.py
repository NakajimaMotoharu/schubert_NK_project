import ast
import inspect
import unittest
import pg6250_original4034_artifacts as subject
from pg6042_original3976_artifacts import expected_case_keys


class Definition(unittest.TestCase):
    def test_seven_actual_new_method_identities_not_success_arithmetic(self):
        source='97dd2ba6185143632439f32dfc1d663061f1e55c'
        rows=subject.new_case_identities(source)
        self.assertEqual(7,len(expected_case_keys(rows)))
        self.assertEqual({'dev.codex.schubert.nk.api.messaging.inbound.ConfirmedRollbackCallbackTest',
            'dev.codex.schubert.nk.web.bootstrap.WebManagementServerTest'},{r['class']for r in rows})

    def test_exact_genuine_campaign_only(self):
        import pg6042_original3976_artifacts as reader
        tree=ast.parse(inspect.getsource(reader.inspect_original));found=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Compare)and any(isinstance(op,ast.NotIn)for op in node.ops):
                right=node.comparators[-1]
                if isinstance(right,ast.Tuple):found.append(ast.literal_eval(right))
        self.assertTrue(any(('PG6244',(4034,606,1667),10)in item for item in found))
        self.assertIn(('PG6088','PG6118','PG6196','PG6212','PG6244','PG6272','PG6302','PG6330', 'PG6386', 'PG6408', 'PG6452', 'PG6490'),found)

    def test_original_whole_and_prior_identity_bindings(self):
        values=subject.definitions()['main'].__code__.co_consts
        for item in ('PG6244-six-v1','PG6212-current4027-cases/qualification.json',
            'PG6248-normal-phase-qualification-v1/manifest.json','PG6244-current4034-cases',
            '477bacaf70d4ad8dfe7310af0f85304d1a9fdd42e7f09db31afbbdd83a603166',
            '13e042309e312ee779e67a81a5866f6448138604355b2fccea764b6e914dbb30'):
            self.assertIn(item,values)


if __name__=='__main__':unittest.main()
