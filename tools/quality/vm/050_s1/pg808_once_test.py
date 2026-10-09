import ast,unittest
from pg808_external_once import PAYLOAD

class Test(unittest.TestCase):
 def test_durable_exact_once_before_external_start(self):
  ast.parse(PAYLOAD)
  start="['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service']"
  self.assertEqual(1,PAYLOAD.count(start));self.assertLess(PAYLOAD.index("persist('external-start-guard.private.json'"),PAYLOAD.index(start))
  for value in('pg805-runtime-resume-v2','a1cd83116444d30e0ca2cb974494f0edbe30a73cd233de308c7a68a1d2f79d63','pg805-once-resume.conf',"'originalBudgetSeconds':1800","'repeatForbidden':True","'native-before'","before['coverageBefore']","before['unitFiles'].items()",'9de2d03c-28c7-4647-97d9-c66ace06048c'):
   self.assertIn(value,PAYLOAD)
  for value in('PG495','0.1.0-PG750','systemctl stop','pg492-once-resume.conf'):self.assertNotIn(value,PAYLOAD)

if __name__=='__main__':unittest.main()
