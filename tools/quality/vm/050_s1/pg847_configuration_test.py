import unittest
from pg847_configuration import FIELDS,same
class Test(unittest.TestCase):
 def test_full_literal_union_and_all_mutations(self):
  expected=set('Id Type Restart RemainAfterExit KillMode SendSIGKILL TimeoutStartUSec TimeoutStopUSec ExecStart ExecStop User Group SupplementaryGroups NoNewPrivileges CapabilityBoundingSet AmbientCapabilities ProtectSystem ProtectHome PrivateTmp PrivateDevices RestrictAddressFamilies ReadWritePaths ReadOnlyPaths Requires After FragmentPath DropInPaths RestrictSUIDSGID UMask LimitCORE MemoryMax TasksMax'.split())
  self.assertEqual(expected,FIELDS);self.assertEqual(32,len(FIELDS))
  before={k:'independent-'+k for k in expected};parse=lambda _:None
  self.assertTrue(same(before,dict(before),parse))
  for k in expected:
   after=dict(before);after[k]='changed'
   self.assertFalse(same(before,after,parse),k)
   after=dict(before);del after[k];self.assertFalse(same(before,after,parse))
  for a,b in((None,before),(before,None),({},before),(before,{**before,'foreign':'value'}),(before,{**before,'UMask':None})):
   self.assertFalse(same(a,b,parse))
 def test_declared_triple_distinct_from_auxiliary_history(self):
  before={k:'same' for k in FIELDS};after=dict(before);after['ExecStart']='history-new';after['ExecStop']='stop-history-new'
  parse=lambda x:('/fixed',['/fixed','arg'],False,'new'if'new'in x else'old')
  self.assertTrue(same(before,after,parse))
  self.assertFalse(same(before,after,lambda x:('/foreign'if'new'in x else'/fixed',[],False)))
if __name__=='__main__':unittest.main()
