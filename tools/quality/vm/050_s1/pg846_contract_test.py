"""Independent actual-new-cohort oracle joins and rejected false terminal receipts."""
import ast,datetime,unittest
from pathlib import Path
import pg846_capture_done as p
class Test(unittest.TestCase):
 def test_actual_full_join_no_old_authority(self):
  raw=p.payload();ast.parse(raw)
  for v in('3417355','9c08566fff9945a492eaae25559c3084','175948','171417627031',p.AFTER,p.RUN,'2026-10-09T05:42:22.532331Z','0.1.0-PG832','2a0d5aa392c85a1dc12a1cdb423978e8500895b8',"len(m.TABLES)==24",'pg846-completed-readonly-v1'):self.assertIn(v,raw)
  for v in('pg650','PG631','systemctl start','systemctl stop','bounds'):self.assertNotIn(v,raw)
 def test_pid1_root_original_budget_independent_literals(self):
  raw=(Path(__file__).resolve().parent/'pg609_parent_receipt.py').read_text();nodes=[n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)]
  env={'datetime':datetime,'BOOT':'cc9ed8747f4f450ea1888de1e42c8441','INV':'9c08566fff9945a492eaae25559c3084','JOB':'175948','START':171417627031,'RUN':p.RUN,'CUTOFF':'2026-10-09T05:42:22.532331Z','ACT':'021111b4-6de5-4733-917d-5ac176240ffc'}
  exec(compile(ast.Module(body=nodes,type_ignores=[]),'<same actual pure completion>','exec'),env)
  stamp=datetime.datetime(2026,10,9,15,20,tzinfo=datetime.timezone.utc)
  base={'_BOOT_ID':env['BOOT'],'_PID':'1','_UID':'0','_COMM':'systemd','UNIT':'schubert-nk-morning-controller.service','INVOCATION_ID':env['INV'],'__MONOTONIC_TIMESTAMP':'171897627031','__REALTIME_TIMESTAMP':str(int(stamp.timestamp()*1000000))}
  rows=[{**base,'__CURSOR':'one','MESSAGE_ID':'39f53479d3a045ac8e11786248231fbf','JOB_ID':'175948','JOB_TYPE':'start','JOB_RESULT':'done'},{**base,'__CURSOR':'two','MESSAGE_ID':'7ad2d189f7e94e70a38c781354912448'}]
  done=('NKDONE1\n'+p.RUN+'\n2026-10-09T05:42:22.532331Z\n021111b4-6de5-4733-917d-5ac176240ffc\n2026-10-09T15:19:59.000000Z\n0\n').encode()
  self.assertEqual(480,env['completed'](rows,done)['elapsedSeconds'])
  for key,value in(('_PID','3417355'),('_UID','1'),('INVOCATION_ID','7ea672e8a76c4a4a8a7994652366a4cc'),('__MONOTONIC_TIMESTAMP','173217627032'),('JOB_RESULT','timeout'),('JOB_ID','162013'),('__CURSOR','two')):
   changed=[dict(r)for r in rows];changed[0][key]=value
   with self.assertRaises(ValueError):env['completed'](changed,done)
  for bad in(done.replace(b'\n0\n',b'\n143\n'),done.replace(p.RUN.encode(),b'55ac70e7-0180-4c32-8c91-5a379ebedf24'),None,b''):
   with self.assertRaises(ValueError):env['completed'](rows,bad)
if __name__=='__main__':unittest.main()
