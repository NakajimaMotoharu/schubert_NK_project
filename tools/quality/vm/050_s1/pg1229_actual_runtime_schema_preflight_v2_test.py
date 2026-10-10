import ast
import unittest
import pg1227_actual_runtime_schema_preflight as old
import pg1229_actual_runtime_schema_preflight_v2 as new

class TraceTest(unittest.TestCase):
    def test_final_literal_run_and_newonly_slot_source(self):
        for module,expected in [(old,'PG1227-runtime-schema-preflight-v1'),(new,'PG1229-runtime-schema-preflight-v2')]:
            s=module.payload();t=ast.parse(s);found=[]
            for n in ast.walk(t):
                if isinstance(n,ast.Dict):
                    for k,v in zip(n.keys,n.values):
                        if isinstance(k,ast.Constant)and k.value=='run'and isinstance(v,ast.Constant):found.append(v.value)
            self.assertEqual(found,[expected]);compile(s,'<actual readonly trace>','exec')
            self.assertFalse("'run':'PG1222-completed-retirement-preflight-v1'"in s)

if __name__=='__main__':unittest.main()
