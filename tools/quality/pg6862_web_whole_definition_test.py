import ast
import unittest
import pg6862_web_deadline_whole as p
import pg6864_original4209_artifacts as read


class Web4209WholeDefinitionTest(unittest.TestCase):
    def test_all_independent_declarations_and_six_new_identities(self):
        self.assertIsNotNone(p.declared_inventory())
        rows=read.added_cases(p.original_source())
        self.assertEqual((6,6),(len(rows),len({(r['class'],r['caseNameSha256'])for r in rows})))

    def test_complete_current_runner_namespace_and_dimensions(self):
        raw=p.server_source('0'*40,'1'*64);tree=ast.parse(raw)
        ints=[x.value for x in ast.walk(tree)if isinstance(x,ast.Constant)and type(x.value)is int]
        self.assertEqual(2,ints.count(4209));self.assertEqual(1,ints.count(653))
        self.assertIn('PG6862-six-v1',raw);self.assertNotIn('PG6828-six-v1',raw)
        self.assertIn('4209',p.driver_source({}));self.assertIn('PG6862',read.emitted('0'*64,'/tmp/definition-only'))


if __name__=='__main__':unittest.main()
