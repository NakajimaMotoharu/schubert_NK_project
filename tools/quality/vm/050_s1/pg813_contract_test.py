"""Literal current failed949 parents/epoch/namespace, whole generated closure, no VM."""
import ast
import unittest
import pg813_sources as p

class RecoveryContract(unittest.TestCase):
 def test_fixed_failed_parent_and_missing_foreign_values(self):
  tree=ast.parse(p.helper());names={'BOOT','PARENT','FIELDS'}
  nodes=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in names for t in n.targets)or isinstance(n,ast.FunctionDef)and n.name in('parent_value','epoch_value')]
  env={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual recovery pure guards>','exec'),env)
  parent=dict.fromkeys(env['FIELDS'],'')
  parent.update(Id='schubert-nk-morning-controller.service',LoadState='loaded',InvocationID='7ea672e8a76c4a4a8a7994652366a4cc',Result='timeout',ExecMainCode='1',ExecMainStatus='143',ActiveState='failed',SubState='failed',MainPID='0',ControlPID='0',Job='',ExecMainStartTimestampMonotonic='155954641282')
  self.assertTrue(env['parent_value'](parent));self.assertFalse(env['parent_value'](None))
  for key in parent:
   for variant in(None,'foreign'):
    changed=dict(parent);changed[key]=variant
    if key in('Id','LoadState','InvocationID','Result','ExecMainCode','ExecMainStatus','ActiveState','SubState','MainPID','ControlPID','Job','ExecMainStartTimestampMonotonic')or variant is None:self.assertFalse(env['parent_value'](changed))
  raw=b'NKEPOCH1\nstate=ISSUED\nboot_id=cc9ed874-7f4f-450e-a188-8de1e42c8441\nepoch_id=0eece14c-f832-47c2-b7dd-14125682e7ea\nrun_id=9de2d03c-28c7-4647-97d9-c66ace06048c\ncutoff_utc=2026-10-09T05:42:22.532331Z\nactivation_id=021111b4-6de5-4733-917d-5ac176240ffc\npermit_sha256='+b'a'*64+b'\n'
  self.assertTrue(env['epoch_value'](raw,False));self.assertFalse(env['epoch_value'](raw,True))
  self.assertTrue(env['epoch_value'](raw.replace(b'ISSUED',b'INVALID').replace(b'a'*64,b'-'),True))
  for needle in(b'0eece14c-f832-47c2-b7dd-14125682e7ea',b'2026-10-09T05:42:22.532331Z',b'cc9ed874-7f4f-450e-a188-8de1e42c8441'):
   self.assertFalse(env['epoch_value'](raw.replace(needle,b'foreign'),False))
 def test_retirement_is_read_only_repeatable_and_exact_capture(self):
  raw=p.helper();self.assertIn("if action=='retirement':return",raw)
  self.assertIn('pg812-current-timeout-v4/current.private.json',raw);self.assertIn('len(value[\'rows\'][\'schubert.batch_runs\'])==554',raw)
  self.assertNotIn('pg777-failure-full758-v1',raw)
  self.assertNotIn("'start',",raw)
 def test_liveness_and_same_current_production_namespace(self):
  raw=p.java();self.assertIn('names().size()==44',raw);self.assertIn('retiredNames().size()==43',raw)
  self.assertIn('databaseScope=new Pg798DatabaseScope',raw);self.assertIn('batchLease.confirmClosed();schemaLease.confirmClosed()',raw)
  self.assertIn('while(!process.waitFor(250',raw);self.assertIn('pulse();',raw)
  self.assertIn('RootFailedStartRecovery.quarantinePair',raw);self.assertIn('RootFailedStartRecovery.retirePair',raw)
  self.assertNotIn('PG750',raw);self.assertIn('rows()==554',raw)

if __name__=='__main__':unittest.main()
