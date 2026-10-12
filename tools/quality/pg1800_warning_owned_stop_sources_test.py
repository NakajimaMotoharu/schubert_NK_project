"""Actual emitted guard/function, independent observed failure and counterexamples."""
import ast
import hashlib
import json
import unittest
from unittest.mock import Mock
from pg1800_warning_owned_stop_sources import sources
from pg1799_warning_parent_projection_contract_test import Parent


class Emitted(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual=sources()
        cls.projection={}
        exec(cls.actual['pg1800_warning_parent_projection.py'],cls.projection)

    def fixture(self):return Parent().fixture()

    def test_capture_actual_guard_all_fields(self):
        tree=ast.parse(self.actual['pg1800_native_refs.py'])
        nodes=[n for n in ast.walk(tree)if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id=='qualify_warning_parent']
        self.assertEqual(1,len(nodes))
        code=compile(ast.Module(body=nodes,type_ignores=[]),'<actual Ref guard>','exec')
        fields=self.fixture();exec(code,{**self.projection,'parent':fields})
        for key in self.projection['EXPECTED']:
            with self.subTest(key=key),self.assertRaises(ValueError):exec(code,{**self.projection,'parent':{**fields,key:None}})

    def receipt(self,fields,completion=None):
        tree=ast.parse(self.actual['pg1800_native_owned_stop.py'])
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='parent_receipt')
        self.assertEqual(1,len([n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='parent_receipt']))
        done={'genuinePid1Failure':True,'genuinePid1StartDone':False,'genuineRootDone':True,'managerFailureRetained':True,'completionOutcome':'WARNING','endMonotonicUs':83018953880}
        def require(value):
            if not value:raise ValueError('guard refused')
        path=Mock();path.exists.return_value=False;path.read_bytes.return_value=b'independent-original'
        saved={};kernel=Mock()
        ns={**self.projection,'holder':lambda:123,'command':lambda _:b'{"INVOCATION_ID":"b5a12ee25dc44ec49b08f5d084b4052f","JOB_RESULT":"failed"}\n','BOOT':'3d69f5af-6bac-46b1-a540-7591c4a79a0d','json':json,'unique':dict,'pathlib':Mock(Path=Mock(return_value=path)),'completed':lambda rows,original:done if completion is None else completion,'require':require,'show':lambda _:fields,'kernel_empty':kernel,'save':lambda name,data:saved.__setitem__(name,data),'hashlib':hashlib}
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual parent_receipt>','exec'),ns)
        ns['parent_receipt']();return saved,kernel

    def test_actual_receipt_preserves_failure_no_success(self):
        saved,kernel=self.receipt(self.fixture());kernel.assert_called_once_with('schubert-nk-morning-controller.service')
        result=json.loads(saved['parent.normal.private'])
        self.assertFalse(result['actualPid1JobDone']);self.assertFalse(result['parentOrdinaryExit0']);self.assertTrue(result['managerFailureRetained'])
        for key in self.fixture():
            with self.subTest(key=key),self.assertRaises(ValueError):self.receipt({**self.fixture(),key:None})
        with self.assertRaises(ValueError):self.receipt(self.fixture(),{'genuinePid1Failure':False})

    def test_whole_source_namespace_and_negative_parent_success_removed(self):
        self.assertEqual(15,len(self.actual))
        for name,raw in self.actual.items():
            with self.subTest(name=name):self.assertFalse('1772'in raw)
        receipt=self.actual['pg1800_native_owned_stop.py']
        node=next(n for n in ast.parse(receipt).body if isinstance(n,ast.FunctionDef)and n.name=='parent_receipt')
        text=ast.get_source_segment(receipt,node)
        self.assertFalse("JOB_RESULT')=='done'"in text);self.assertFalse("fields['Result']=='success'"in text)


if __name__=='__main__':unittest.main()
