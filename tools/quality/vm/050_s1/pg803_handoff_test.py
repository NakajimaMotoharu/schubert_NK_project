import ast
import unittest
from pg803_published_handoff import payload

class Test(unittest.TestCase):
 def test_new_current_guard_not_old_guard_or_success_inference(self):
  from pg803_handoff_v2 import payload as current
  raw=current();ast.parse(raw)
  self.assertIn('h.parent=current_parent',raw)
  self.assertIn("h.parent_value(h.show(h.EXTRA[0]))",raw)
  self.assertIn('c48af3ada5e2f00b1704f65fdb4625d6220bed29b6cecbbd23d7354cf708880d',raw)
  self.assertNotIn('0.1.0-PG750',raw)
  self.assertIn('pg803-published-handoff-v2',raw)
 def test_exact_current_cohort_and_preservation(self):
  raw=payload();ast.parse(raw)
  for value in('3112993,15339690','3113102,15340179','0.1.0-PG796','publication.approval_only','old-epoch.private','signal.SIGTERM','before==h.snapshot()','after==before==h.snapshot()'):
   self.assertIn(value,raw)
  for value in('3112232','15308543','0.1.0-PG750','SIGKILL','systemctl start','systemctl stop'):self.assertNotIn(value,raw)

if __name__=='__main__':unittest.main()
