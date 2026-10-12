import unittest
from pg1528_filesystem_full_six import server_source,PRODUCTION

class CurrentFullAdmissionTest(unittest.TestCase):
 def test_exact_all_six_no_skip_or_missing_pass_and_new_source(self):
  raw=server_source('a'*40,'b'*64);ns={'__name__':'compile_only'};exec(compile(raw,'<full admission>','exec'),ns)
  good=[0,True,[],3582,524,1637];self.assertTrue(ns['complete_result'](*good))
  for i,invalid in {0:[143,1,None,True],1:[False,None,1],2:[None,['failed']],3:[3578,3581,3583,0],4:[523,525],5:[1635,1636,1638]}.items():
   for x in invalid:
    v=good.copy();v[i]=x;self.assertFalse(ns['complete_result'](*v))
  self.assertIn(PRODUCTION,raw)
  self.assertEqual(['protocol','storage','bootstrap','api','web','batch'],ns['MODULES'])
  for forbidden in ['-am','-Dtest=','-DskipTests','-DfailIfNoTests=false','StartUnit','StopUnit']:self.assertNotIn(forbidden,raw)
  for required in ['SCHUBERT_SHELLCHECK','SCHUBERT_PG_ROOT','umask=0o027','PG1528-source.tar']:self.assertIn(required,raw)
if __name__=='__main__':unittest.main()
