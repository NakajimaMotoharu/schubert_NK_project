"""Independent construction/24table read/unknown owner refusal, no VM writes."""
import ast
import json
import unittest
from pg773_failure_full import payload,source
from pg772_namespace_test import Test as NamespaceTest


class Test(unittest.TestCase):
    def test_fixed_newcapture_binding(self):
        raw=source();p=payload();ast.parse(p)
        self.assertIn('pg773-failure-full758-v1',raw)
        self.assertNotIn('pg772-failure-current758-v1',raw)
        for text in ('e9f11f1c-f087-458a-aad0-8c1e4e140571','full24Preserved','currentStartupFiles','privateBytes','NoNewPrivs','CapAmb','full-rows.private.json'):
            self.assertIn(text,p)
        self.assertNotIn("['systemctl','stop'",p)
        self.assertNotIn('revoke(',p)

    def test_independent_rows_function(self):
        tree=ast.parse(payload());definition=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='rows')
        tables={'schubert.batch_runs':[{'id':'literal'}],**{'literal.t'+str(i):[]for i in range(23)}}
        commands=[]
        def command(args,maximum):
            commands.append((args,maximum))
            return b'\n'.join(json.dumps({'table':k,'rows':v}).encode()for k,v in sorted(tables.items()))
        env={'expected_rows':tables,'command':command,'json':json}
        exec(compile(ast.Module(body=[definition],type_ignores=[]),'<independent read24>','exec'),env)
        self.assertEqual(tables,env['rows']());sql=commands[0][0][-1]
        self.assertIn('repeatable read read only',sql);self.assertIn('commit;',sql)
        self.assertEqual(24,sql.count('select json_build_object'))
        self.assertNotIn('insert ',sql);self.assertNotIn('update ',sql)
        env['command']=lambda *_:b'{"table":"foreign","rows":[]}'
        with self.assertRaises(AssertionError):env['rows']()
        env['expected_rows']={'x;delete':[]}
        with self.assertRaises(AssertionError):env['rows']()


if __name__=='__main__':
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(Test),unittest.defaultTestLoader.loadTestsFromTestCase(NamespaceTest)])
    raise SystemExit(not unittest.TextTestRunner().run(suite).wasSuccessful())
