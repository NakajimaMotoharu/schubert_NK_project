import ast
import unittest
from pg1194_completed_resume_receipt_v2 import payload


class ReceiptProjectionTest(unittest.TestCase):
    def test_actual_generated_projection_keeps_all_fields_and_raw(self):
        s=payload();t=ast.parse(s)
        nodes=[n for n in t.body if isinstance(n,ast.Import)and any(a.name=='json'for a in n.names)or isinstance(n,ast.FunctionDef)and n.name in {'pairs','project'}]
        env={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual receipt projection>','exec'),env)
        a=b'{"__CURSOR":"one","MESSAGE":"literal"}\n';b=b'{"MESSAGE":"literal","__CURSOR":"one"}\n'
        self.assertEqual(env['project'](a),env['project'](b))
        self.assertNotEqual(env['project'](a),env['project'](a.replace(b'literal',b'changed')))
        for bad in [None,b'{"__CURSOR":null}',b'{"__CURSOR":"one","__CURSOR":"two"}',a+a]:
            with self.assertRaises(ValueError):env['project'](bad)
        for part in ['project(again)!=project(raw)', 'rows=json.loads(project(raw))','journal-first.private.jsonl','journal-second.private.jsonl','result=qualify(BINDING,rows,done)']:
            self.assertTrue(part in s,part)


if __name__=='__main__':unittest.main()
