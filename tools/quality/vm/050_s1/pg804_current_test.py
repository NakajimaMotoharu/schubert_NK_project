import ast
import unittest
from pg804_current_sources import java,helper,SOURCE,DIGEST
from pg804_current_compile import source as compiler,refs_source
from pg804_current_native import source as native

class Test(unittest.TestCase):
 def test_all_surface_current_phase_not_stale_old_candidate(self):
  for raw in(helper(),compiler(),native(),refs_source()):ast.parse(raw)
  for value in(SOURCE,DIGEST,'"PG796"','pg804-current-tools-v1','Pg804CurrentReadback','PG804-fixed-recovery','PG804-fixed-snapshot','Pg798DatabaseScope','pg804_owned.py'):
   self.assertIn(value,java())
  for value in('0.1.0-PG750','8d4b68b4f1449932ebe506aaf08e584bbfea8dd2','PG798','pg798','Pg798DatabaseProbe'):
   self.assertNotIn(value,java());self.assertNotIn(value,native())
  self.assertIn('pg803-published-handoff-v2/after.private.json',helper())
  self.assertIn('Pg804WiringTest.java',compiler());self.assertIn('Pg804WiringTest',compiler())
  self.assertIn('0.1.0-PG796',native());self.assertIn('0.1.0-PG796',helper())
  self.assertNotIn("'stop'",helper());self.assertIn('batchLease.confirmClosed();schemaLease.confirmClosed();',java())

if __name__=='__main__':unittest.main()
