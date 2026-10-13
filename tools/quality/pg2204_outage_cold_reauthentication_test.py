import ast
import unittest
import pg2204_outage_cold_reauthentication as p


class ColdProof(unittest.TestCase):
    def test_whole_export_and_no_business_operations(self):
        s=p.payload();tree=ast.parse(s)
        self.assertIn("SEALED='f109a515cbd67998aeee38de102c0cceacdb9b95fbe0e4b7b09645d83821f27a'",s)
        self.assertIn("boot!='3d69f5af-6bac-46b1-a540-7591c4a79a0d'",s)
        self.assertIn("rows==old['rows'] and len(rows)==24",s)
        self.assertIn("durable==old['durable']",s)
        self.assertIn("'oldOwnedStopAccepted':False",s)
        self.assertNotIn('kill(',s);self.assertNotIn("'start'",s);self.assertNotIn("'stop'",s)
        functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='cold']
        ns={};exec(compile(ast.Module(body=functions,type_ignores=[]),'<independent cold fixture>','exec'),ns)
        fixture={'LoadState':'loaded','ActiveState':'inactive','SubState':'dead','MainPID':'0',
          'ControlPID':'0','Job':'','InvocationID':'','Result':'success','KillMode':'control-group',
          'SendSIGKILL':'no','ExecMainCode':'0','ExecMainStatus':'0','ExecMainStartTimestampMonotonic':'0',
          'ExecMainExitTimestampMonotonic':'0'}
        self.assertTrue(ns['cold'](fixture))
        for k,v in [('InvocationID','old'),('Job','1'),('MainPID','1'),('Result','timeout'),('ExecMainStatus','143'),('ExecMainStartTimestampMonotonic','1'),('ActiveState','active')]:
            self.assertFalse(ns['cold']({**fixture,k:v}),k)


if __name__=='__main__':unittest.main()
