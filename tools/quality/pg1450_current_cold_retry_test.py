"""Fresh family independent binding and executable static namespace oracle."""
import ast
import unittest
from pg1450_current_cold_retry import java,observer
from pg1441_current_cold_sources_test import ColdSourceTest


class RetrySourceTest(unittest.TestCase):
    def test_new_only_binding(self):
        s=java();p=observer()
        self.assertIn('Pg1450CurrentColdPreparation',s)
        self.assertIn('pg1450-current-cold-tools-v1',s)
        self.assertIn('pg1452-current-cold-prepared-v1',s)
        self.assertIn('pg1452-current-cold-prepared-v1',p)
        self.assertNotIn('pg1441-current-cold-',s+p)
        self.assertNotIn('Pg1441CurrentColdPreparation',s+p)
        self.assertIn('3d69f5af-6bac-46b1-a540-7591c4a79a0d',s+p)

    def test_generated_prefix_exec_before_config_use(self):
        tree=ast.parse(observer());nodes=[]
        names={'CAPTURE_BOUND','UNIT_VECTOR','CONFIG_CONTRACT','CONFIG_FIELDS'}
        for n in tree.body:
            if isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)and t.id in names for t in n.targets):nodes.append(n)
            elif isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id=='exec'and len(n.value.args)==2 and isinstance(n.value.args[1],ast.Name)and n.value.args[1].id in names:nodes.append(n)
        ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<fresh prefix>','exec'),ns)
        self.assertEqual(32,len(ns['CONFIG_FIELDS']))
        self.assertTrue(ns['CAPTURE_BOUND']['accepted'](0,36343264,67108864))
        self.assertFalse(ns['CAPTURE_BOUND']['accepted'](0,67108865,67108864))
        self.assertFalse(ns['UNIT_VECTOR']['matches'](None,None,None))


if __name__=='__main__':unittest.main()
