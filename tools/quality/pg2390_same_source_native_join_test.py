"""Independent literals for immutable source/class/window admission, no remote execution."""
import ast
import unittest
from pg2390_same_source_native_join import payload


class Join(unittest.TestCase):
    def test_actual_server_main_byte_proof_latest_only_and_no_vm(self):
        raw=payload();tree=ast.parse(raw)
        for text in ['PG2284-native-v1','PG2384-native-v1','PG2300-six-v1','images[0]==images[1]','main_count==1643','len(streams)==18',"len({s['sessionIdSha256']for s in sessions})==18","if i!=inspector[1]","'oldSourceNativeImported':False","'formalAccepted':False"]:self.assertIn(text,raw)
        self.assertNotIn('PG2048',raw);self.assertNotIn('0fd734',raw)
        for n in ast.walk(tree):
            if isinstance(n,ast.List):self.assertFalse({'ssh','systemctl','start','stop','restart','daemon-reload'}&{getattr(v,'value',None)for v in n.elts if isinstance(v,ast.Constant)})
        expr=next(n.args[0]for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='require'and ast.get_source_segment(raw,n)=='require(images[0]==images[1])')
        code=compile(ast.Expression(expr),'<independent all-class hash bridge>','eval')
        for a,b,w in [({'a':'same'},{'a':'same'},True),({'a':'same'},{'a':'foreign'},False),({'a':'same'},{},False),({'a':'same'},{'a':'same','extra':'same'},False)]:self.assertEqual(w,eval(code,{'images':[a,b]}))


if __name__=='__main__':unittest.main()
