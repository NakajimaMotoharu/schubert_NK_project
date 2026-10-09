"""Independent fake completion only tests pure generation; no actual acceptance/authority."""
import unittest
import pg847_stop_binding as p
def fixture():
 return {'actualExit':0,'productionSource':p.SOURCE,'batchRun':'9de2d03c-28c7-4647-97d9-c66ace06048c','cutoff':'2026-10-09T05:42:22.532331Z','activation':'021111b4-6de5-4733-917d-5ac176240ffc','genuineCompletion':{'genuinePid1StartDone':True,'genuineRootDone':True,'endMonotonicUs':172017627031},'beforeSha256':'a'*64,'parentEndedUTC':'2026-10-09T15:21:57.000000Z','ownedUnits':{u:{'MainPID':str(4000000+i),'InvocationID':str(i+1).zfill(32),'ActiveState':'active','SubState':'running'}for i,u in enumerate(('caddy.service','schubert-nk-web.service','schubert-nk-api.service','artemis.service'))}}
class Test(unittest.TestCase):
 def test_whole_new_source_generation_current_lease(self):
  files=p.generate(fixture());java=files['Pg847NativeStop.java'];refs=files['pg847_native_refs.py']
  for v in('Pg797OwnedDatabase.Expected(pid,"schubert_batch","PG847-native-stop","schubert_nk",true,true)','lease.confirmClosed()','maxGapNanos','Pg387TrustedDeployment.LABEL="PG832"',p.SOURCE,p.DIGEST,'2026-10-09T15:21:57.000000Z'):
   self.assertIn(v,java)
  self.assertNotIn('Pg464CodeOnlyDeployment',java)
  for v in('pg846-completed-readonly-v1','9c08566fff9945a492eaae25559c3084','171417627031',p.SOURCE,p.DIGEST,'from pg847_configuration import FIELDS as CONFIG_FIELDS,same as config_same',"signed_cfg=json.loads(original)['configuration']"):
   self.assertIn(v,refs)
  self.assertIn('pg847_configuration.py',files)
  self.assertNotIn('systemctl start',refs)
 def test_foreign_sources_failed_done_and_outside_original_budget(self):
  for key,value in(('actualExit',143),('productionSource','102cdf1d365ab321f74b523237590eee764ae858'),('batchRun','55ac70e7-0180-4c32-8c91-5a379ebedf24'),('activation','7d381b67-b37b-48c6-99ac-e04a336f887d')):
   f=fixture();f[key]=value
   with self.assertRaises(ValueError):p.generate(f)
 def test_transport_newonly_whole_closure_and_genuine_precondition(self):
  import ast
  import pg847_native_stop as transport
  raw=transport.source();ast.parse(raw)
  for v in('pg847-native-tools-v1','pg847-frozen-v1.safe.json','pg847-stage-v1.exit','pg846-completed-readonly-v1.exit','pg849-chr-a01-native-v1.exit','Pg847NativeArgumentTest','Pg847NativeStop stop','0.1.0-PG832',"sys.argv[1]in ('stage','stop')"):
   self.assertIn(v,raw)
  for v in('Pg847NativeStopTest','Pg841','Pg778','Pg464CodeOnlyDeployment','systemctl start','prepare\')'):
   self.assertNotIn(v,raw)
  for key,value in(('genuineRootDone',False),('genuinePid1StartDone',False),('endMonotonicUs',173217627032),('endMonotonicUs',171417627030)):
   f=fixture();f['genuineCompletion'][key]=value
   with self.assertRaises(ValueError):p.generate(f)
if __name__=='__main__':unittest.main()
