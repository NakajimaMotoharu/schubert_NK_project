import copy
import unittest
from pg577_same_day_oracle import STEPS,OLD_RUN,RUN,verify


class Test(unittest.TestCase):
    def setUp(self):
        self.before=[]
        for n in range(462):self.before.append({'id':n+1,'step':'CLEAN_LOG','business_date':'2026-10-07','attempt':n%99+1,'status':'SUCCESS'})
        base={'attempt':1,'business_date':'2026-10-08','byte_count':10,'ended_at':'2026-10-08T04:27:00Z','error_code':None,'error_summary':None,'expiry_after_count':None,'expiry_before_count':None,'expiry_cutoff_at':None,'failure_count':0,'run_id':OLD_RUN,'started_at':'2026-10-08T04:03:00Z','status':'SUCCESS','success_count':1,'target_count':1}
        for n,step in enumerate(STEPS):self.before.append({**base,'id':463+n,'step':step})
        self.after=copy.deepcopy(self.before)
        for n,step in enumerate(STEPS):
            backup=n<2;count=n+1 if backup else 0
            self.after.append({**base,'id':473+n,'step':step,'attempt':2,'run_id':RUN,'started_at':'2026-10-08T07:36:30Z','ended_at':'2026-10-08T07:36:35Z'if backup else '2026-10-08T07:36:30Z','status':'SUCCESS'if backup else 'SKIPPED','error_code':None if backup else 'ALREADY_SUCCESSFUL','error_summary':None if backup else 'step already successful for business date','target_count':count,'success_count':count,'byte_count':10 if backup else 0})
    def test_independent_same_day_and_mutated_skip_columns(self):
        result=verify(self.before,self.after,'2026-10-08T07:36:20Z');self.assertEqual(result['newDomainAlreadySuccessfulSkips'],8);self.assertEqual(result['oldBatchRowsPreserved'],472)
        for key,bad in [('status','SUCCESS'),('error_code','BACKUP_UNAVAILABLE'),('error_summary',None),('success_count',1),('target_count',True),('byte_count',1),('attempt',1),('run_id',OLD_RUN),('ended_at','2026-10-08T07:36:31Z'),('expiry_before_count',0)]:
            actual=copy.deepcopy(self.after);actual[475][key]=bad
            with self.assertRaises(ValueError):verify(self.before,actual,'2026-10-08T07:36:20Z')
    def test_missing_duplicate_null_old_row_and_backup_negative(self):
        for actual in (None,self.after[:-1],[*self.after[:-1],self.after[-2]],[*self.after[:-1],None]):
            with self.assertRaises(ValueError):verify(self.before,actual,'2026-10-08T07:36:20Z')
        for index,key,value in [(0,'status','FAILED'),(472,'byte_count',0),(473,'status','SKIPPED'),(473,'ended_at','2026-10-08T07:36:36Z')]:
            actual=copy.deepcopy(self.after);actual[index][key]=value
            with self.assertRaises(ValueError):verify(self.before,actual,'2026-10-08T07:36:20Z')
        with self.assertRaises(ValueError):verify(self.before,self.after,None)


if __name__=='__main__':unittest.main()
