"""Synthetic independent tuple fixtures only; no execution/acceptance authority."""
import copy,unittest
import pg877_stop_binding as p
def fixture():
 return {'actualExit':0,'productionSource':p.SOURCE,'batchRun':p.RUN,'cutoff':p.CUTOFF,'activation':p.ACT,'genuineCompletion':{'genuinePid1StartDone':True,'genuineRootDone':True,'endMonotonicUs':184317014132},'beforeSha256':'b'*64,'parentEndedUTC':'2026-10-09T18:46:44.362279Z','ownedUnits':{u:{'MainPID':str(4000000+i),'InvocationID':str(i+1).zfill(32),'ActiveState':'active','SubState':'running'}for i,u in enumerate(('caddy.service','schubert-nk-web.service','schubert-nk-api.service','artemis.service'))}}
class Test(unittest.TestCase):
 def test_whole_closure(self):
  files=p.generate(fixture());java=files['Pg877NativeStop.java'];refs=files['pg877_native_refs.py']
  for v in (p.SOURCE,p.DIGEST,p.RUN,p.CUTOFF,p.ACT,'lease.confirmClosed()','PG877-native-stop','maxGapNanos','Pg387TrustedDeployment.LABEL="PG862"'):
   self.assertIn(v,java)
  for v in (p.INV,str(p.START),'pg875-completed-readonly-v1',"signed_cfg=json.loads(original)['configuration']",'manager.LoadUnit(u);manager.RefUnit(u)','complete_configuration(', 'len(old)==24'):
   self.assertIn(v,refs)
  for name,raw in files.items():
   for stale in ('Pg847','pg847','PG832','9de2d03c-28c7-4647-97d9-c66ace06048c','9c08566fff9945a492eaae25559c3084','2a0d5aa392c85a1dc12a1cdb423978e8500895b8','Pg464CodeOnlyDeployment'):
    self.assertNotIn(stale,raw,name)
 def test_negative_fixed_receipt(self):
  for key,value in (('actualExit',143),('productionSource','0'*40),('batchRun','9de2d03c-28c7-4647-97d9-c66ace06048c'),('activation','021111b4-6de5-4733-917d-5ac176240ffc'),('cutoff','2026-10-09T05:42:22.532331Z'),('parentEndedUTC','2026-10-09T18:20:00.000000Z'),('beforeSha256',None)):
   f=fixture();f[key]=value
   with self.assertRaises((ValueError,TypeError)):p.generate(f)
  for key,value in (('genuineRootDone',False),('genuinePid1StartDone',False),('endMonotonicUs',p.START-1),('endMonotonicUs',p.DEADLINE+1)):
   f=fixture();f['genuineCompletion'][key]=value
   with self.assertRaises(ValueError):p.generate(f)
 def test_all_owned_actors(self):
  for field,value in (('MainPID','0'),('InvocationID',''),('ActiveState','inactive'),('SubState','exited')):
   f=fixture();f['ownedUnits']['schubert-nk-api.service'][field]=value
   with self.assertRaises(ValueError):p.generate(f)
 def test_full_configuration(self):
  import pg847_configuration as c
  values=p.generate(fixture());env={}
  exec(compile(values['pg877_configuration_capture.py'],'<pure typed configuration definitions>','exec'),env)
  self.assertEqual(c.FIELDS,env['FIELDS'])
  raw=''.join(k+'='+('z.service a.service' if k=='After' else '')+'\n' for k in sorted(c.FIELDS))
  self.assertEqual(env['configuration_value'](raw)['After'],'a.service z.service')
  for bad in (None,raw+'Unknown=\n',raw.replace('ExecStop=\n',''),raw.replace('After=z.service a.service','After=a.service a.service')):
   with self.assertRaises(ValueError):env['configuration_value'](bad)
 def test_transport_closure(self):
  import ast
  import pg877_native_stop as transport
  raw=transport.source();ast.parse(raw)
  for val in ('pg877-native-tools-v1','pg877-frozen-v1.safe.json','pg875-completed-readonly-v1.exit','pg876-chr-a01-native-v1.exit','Pg877NativeArgumentTest','Pg877NativeStop stop','0.1.0-PG862',"sys.argv[1]in ('stage','stop')"):
   self.assertIn(val,raw)
  for val in ('Pg847','pg847','PG832','systemctl start','Pg877NativeStopTest','verify/recover'):
   self.assertNotIn(val,raw)
if __name__=='__main__':unittest.main()
