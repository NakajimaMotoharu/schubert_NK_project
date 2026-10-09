import ast
import unittest
from pg803_published_handoff import payload

class Test(unittest.TestCase):
 def test_exact_current_cohort_and_preservation(self):
  raw=payload();ast.parse(raw)
  for value in('3112993,15339690','3113102,15340179','0.1.0-PG796','publication.approval_only','old-epoch.private','signal.SIGTERM','before==h.snapshot()','after==before==h.snapshot()'):
   self.assertIn(value,raw)
  for value in('3112232','15308543','0.1.0-PG750','SIGKILL','systemctl start','systemctl stop'):self.assertNotIn(value,raw)

if __name__=='__main__':unittest.main()
