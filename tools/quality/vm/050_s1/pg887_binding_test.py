"""Independent synthetic second-run tuple; wrong first proof is rejected."""
import unittest
import pg887_stop_binding as p
from pg877_binding_test import fixture as previous
def fixture():
 f=previous();f.update(batchRun='93cb976e-c36c-47a3-b9e2-0ad28d2996de',cutoff='2026-10-09T19:07:23.894279Z',activation='0dfe0b7f-0e36-4b81-9086-500d896d1187',parentEndedUTC='2026-10-09T19:26:00.000000Z');f['genuineCompletion']['endMonotonicUs']=186700000000
 return f
class Test(unittest.TestCase):
 def test_whole_new_cohort(self):
  files=p.generate(fixture())
  for name,raw in files.items():
   for old in ('Pg877','pg875','pg877','19022204-8a9e-418d-ba2a-9967ff923dc2','09167719cb0445fea8da5a6fdbaa3b0f','183192933299','3592151'):
    self.assertNotIn(old,raw,name)
  self.assertIn('pg885-completed-readonly-v1',files['pg887_native_refs.py']);self.assertIn('75f48ce36cd740e98a801eede7fdbb7f',files['pg887_native_refs.py'])
  self.assertIn('Pg797OwnedDatabase.Expected(pid,"schubert_batch","PG887-native-stop"',files['Pg887NativeStop.java'])
 def test_first_or_failed_foreign_rejected(self):
  with self.assertRaises(ValueError):p.generate(previous())
  for key,value in (('actualExit',1),('batchRun','19022204-8a9e-418d-ba2a-9967ff923dc2'),('activation',None)):
   f=fixture();f[key]=value
   with self.assertRaises(ValueError):p.generate(f)
  for end in (185542282250,187342282252):
   f=fixture();f['genuineCompletion']['endMonotonicUs']=end
   with self.assertRaises(ValueError):p.generate(f)
if __name__=='__main__':unittest.main()
