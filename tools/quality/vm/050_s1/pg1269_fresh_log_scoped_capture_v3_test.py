import ast
import unittest
from pg1269_fresh_log_scoped_capture_v3 import extend_scope,payload
from pg1260_fresh_backup_independent_capture import SEALS


class MetadataLifetimeTest(unittest.TestCase):
    def test_actual_ast_guard_oracle_and_reverse_close_lifetime(self):
        prefix="log=[]\nrefs=[1,2]\ntry:\n log.append('guard')\nfinally:\n for ref in reversed(refs):log.append(('return',ref))\n log.append('close')\n"
        for failure in [False,True]:
            business="log.append('oracle')\n"+("raise ValueError('refused')\n"if failure else"log.append('post')\n")
            s=extend_scope(prefix,business);e={}
            if failure:
                with self.assertRaises(ValueError):exec(s,e)
            else:exec(s,e)
            self.assertEqual(e['log'],['guard','oracle']+([]if failure else['post'])+[('return',2),('return',1),'close'])
        with self.assertRaises(ValueError):extend_scope('value=1','value=2')

    def test_whole_actual_generated_scope_not_source_string_only(self):
        s=payload(SEALS);n=ast.parse(s);compile(n,'<actual frozen scoped capture>','exec')
        scope=next(t for t in n.body if isinstance(t,ast.Try))
        calls=[x.func.attr for x in ast.walk(scope)if isinstance(x,ast.Call)and isinstance(x.func,ast.Attribute)]
        self.assertIn('verify_fresh',calls)
        self.assertIn('UnrefUnit',[x.func.attr for f in scope.finalbody for x in ast.walk(f)if isinstance(x,ast.Call)and isinstance(x.func,ast.Attribute)])
        self.assertNotIn('save',[t.id for t in ast.walk(scope)if isinstance(t,ast.Name)])
        top_calls=[t.func.attr for t in ast.walk(ast.Module(body=n.body[n.body.index(scope)+1:],type_ignores=[]))if isinstance(t,ast.Call)and isinstance(t.func,ast.Attribute)]
        self.assertIn('mkdir',top_calls)


if __name__=='__main__':unittest.main()
