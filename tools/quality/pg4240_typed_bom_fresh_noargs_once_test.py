import ast
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from pyflakes.api import check
import pg4240_typed_bom_fresh_noargs_once as p


class TypedBomTest(unittest.TestCase):
    def statements(self):
        tree=ast.parse(p.payload({}));scope=next(n for n in tree.body if isinstance(n,ast.With))
        index=next(i for i,n in enumerate(scope.body)if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id=='persist'and n.value.args[0].value=='external-start-guard.private.json')
        return ast.Module(body=scope.body[index-1:index+1],type_ignores=[])

    def test_actual_path_bytes_record_and_rejection_before_persistence(self):
        blob=b'{"fixture":"independent BOM bytes"}\n';digest=hashlib.sha256(blob).hexdigest()
        with tempfile.TemporaryDirectory()as d:
            path=Path(d)/'manifest.json';path.write_bytes(blob)
            for actual,claimed,expected_success in [(blob,digest,True),(b'changed',digest,False),(blob,'f'*64,False)]:
                saved=[]
                def require(value):
                    if not value:raise ValueError('fixture mismatch')
                ns={'manifest':path,'raw':actual,'sha':claimed,'hashlib':hashlib,'require':require,'data':{'source':{'commit':'fixed'}},'summary':{'parentNormal':False},'watch':{'pid':123},'persist':lambda name,v:saved.append((name,v))}
                if expected_success:
                    exec(compile(self.statements(),'<actual complete BOM barrier/record>','exec'),ns)
                    self.assertEqual([('external-start-guard.private.json',{'source':'fixed','manifestSha256':digest,'ordinaryNoargs':True,'oldRunNotResumed':True,'previousFailedRootData':{'parentNormal':False},'originalBudgetSeconds':1800,'attemptReserved':True,'replayAllowed':False,'observer':{'pid':123}})],saved)
                    json.dumps(saved)
                else:
                    with self.assertRaises(ValueError):exec(compile(self.statements(),'<actual BOM barrier/record>','exec'),ns)
                    self.assertEqual([],saved)

    def test_complete_new_entry_namespace_and_no_path_to_hash(self):
        raw=p.payload({});self.assertEqual(0,check(raw,'<typed BOM complete entry>'))
        self.assertTrue("save=base/'pg4240-typed-bom-fresh-noargs-once-v1-prestart'"in raw)
        self.assertTrue("save=base/'pg4240-typed-bom-fresh-noargs-once-v1'"in raw)
        tree=ast.parse(raw)
        self.assertFalse(any(isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='sha256'and n.args and isinstance(n.args[0],ast.Name)and n.args[0].id=='manifest'for n in ast.walk(tree)))


if __name__=='__main__':unittest.main()
