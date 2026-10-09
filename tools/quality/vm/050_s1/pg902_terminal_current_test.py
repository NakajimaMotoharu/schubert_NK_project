"""Literal captured/gc contract with all-field partial/null/foreign negative mutations."""
import unittest
from pg902_terminal_current import current_normal_or_gc
class Test(unittest.TestCase):
 def test_normal_gc_and_each_forbidden_delta(self):
  captured={'Id':'schubert-nk-bootstrap-admin.service','LoadState':'loaded','ActiveState':'inactive','SubState':'dead','Job':'','MainPID':'0','ControlPID':'0','InvocationID':'a'*32,'Type':'oneshot','Restart':'no','RemainAfterExit':'no','Result':'success','ExecMainCode':'1','ExecMainStatus':'20','ExecMainStartTimestampMonotonic':'100','ExecMainExitTimestampMonotonic':'200','KillMode':'control-group','SendSIGKILL':'no'}
  gc={**captured,'InvocationID':'','ExecMainCode':'0','ExecMainStatus':'0','ExecMainStartTimestampMonotonic':'0','ExecMainExitTimestampMonotonic':'0'}
  self.assertTrue(current_normal_or_gc(captured,captured));self.assertTrue(current_normal_or_gc(captured,gc))
  for key in gc:
   for value in (None,'foreign',0):self.assertFalse(current_normal_or_gc(captured,{**gc,key:value}),(key,value))
   self.assertFalse(current_normal_or_gc(captured,{k:v for k,v in gc.items()if k!=key}))
  for key in ('InvocationID','ExecMainCode','ExecMainStatus','ExecMainStartTimestampMonotonic','ExecMainExitTimestampMonotonic'):
   self.assertFalse(current_normal_or_gc(captured,{**gc,key:captured[key]}))
  for value in (None,{},[],{**gc,'foreign':'x'}):self.assertFalse(current_normal_or_gc(captured,value))
  for value in (None,{},gc,{**captured,'ExecMainStatus':'143'},{**captured,'InvocationID':''}):self.assertFalse(current_normal_or_gc(value,gc))
if __name__=='__main__':unittest.main()
