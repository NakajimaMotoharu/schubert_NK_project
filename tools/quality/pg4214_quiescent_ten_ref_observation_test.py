import ast
import unittest
from pyflakes.api import check
import pg4214_quiescent_ten_ref_observation as p


class MetadataTest(unittest.TestCase):
    def test_all_ten_held_before_body_and_reverse_close(self):
        events=[]
        class Manager:
            def LoadUnit(self,n):events.append(('load',n))
            def RefUnit(self,n):events.append(('ref',n))
            def UnrefUnit(self,n):events.append(('unref',n))
        class Bus:
            def close(self):events.append(('busclose',))
        names=tuple('unit'+str(i)for i in range(10))
        with p.metadata_refs(Manager(),Bus(),names):
            self.assertEqual([x for n in names for x in [('load',n),('ref',n)]],events)
            events.append(('body',))
        self.assertEqual([('unref',n)for n in reversed(names)]+[('busclose',)],events[-11:])

    def test_partial_acquisition_or_body_failure_closes_only_acquired_references(self):
        for phase in ['load','ref','body','unref']:
            events=[]
            class Manager:
                def LoadUnit(self,n):
                    if phase=='load'and n=='b':raise ValueError(phase)
                def RefUnit(self,n):
                    if phase=='ref'and n=='b':raise ValueError(phase)
                def UnrefUnit(self,n):
                    events.append(n)
                    if phase=='unref':raise ValueError(phase)
            class Bus:
                def close(self):events.append('closed')
            with self.subTest(phase=phase),self.assertRaises(ValueError):
                with p.metadata_refs(Manager(),Bus(),('a','b')):
                    if phase=='body':raise ValueError(phase)
            self.assertEqual(['a','closed']if phase in ['load','ref']else['b','a','closed']if phase=='body'else['b','closed'],events)

    def test_final_success_saved_only_after_scope_close_no_business_operations(self):
        raw=p.payload();self.assertEqual(0,check(raw,'<ten reference observation>'))
        tree=ast.parse(raw);scope=next(n for n in tree.body if isinstance(n,ast.With))
        success=next(n for n in tree.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Subscript)and isinstance(n.targets[0].slice,ast.Constant)and n.targets[0].slice.value=='newTenMetadataRefsNormalClose')
        self.assertGreater(success.lineno,scope.end_lineno)
        self.assertTrue("'declarationAccepted':False"in raw)
        self.assertFalse(any(isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='terminate'for n in ast.walk(tree)))


if __name__=='__main__':unittest.main()
