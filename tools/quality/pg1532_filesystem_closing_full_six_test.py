import unittest
from pg1532_filesystem_closing_full_six import server_source,PRODUCTION

class CorrectedSourceAdmissionTest(unittest.TestCase):
 def test_new_source_exact_full_totals_and_no_vm_mutation(self):
  raw=server_source('a'*40,'b'*64);ns={'__name__':'compile_only'};exec(compile(raw,'<same source full>','exec'),ns)
  good=[0,True,[],3583,524,1637];self.assertTrue(ns['complete_result'](*good))
  for i,bad in [(0,143),(1,False),(2,['skipped']),(3,3582),(4,523),(5,1635)]:
   v=good.copy();v[i]=bad;self.assertFalse(ns['complete_result'](*v))
  self.assertIn(PRODUCTION,raw);self.assertNotIn('f8770ff083954664b299ba82a9fcd2ae92fbc391',raw)
  for forbidden in ['-DskipTests','-DfailIfNoTests=false','StartUnit','StopUnit']:self.assertNotIn(forbidden,raw)
if __name__=='__main__':unittest.main()
