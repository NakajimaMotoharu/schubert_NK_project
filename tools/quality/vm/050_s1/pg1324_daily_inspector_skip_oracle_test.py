import copy
import datetime
import unittest
from pg1324_daily_inspector_skip_oracle import qualify

def fixture():
    oldrow={'id':100,'run_id':'9f651096-aef9-4fba-90b0-a653e99f035a','business_date':'2026-10-11','step':'CLEAN_INBOX_OUTBOX','attempt':1,'started_at':'2026-10-10T20:00:00Z','ended_at':'2026-10-10T20:01:00Z','status':'SUCCESS','target_count':0,'success_count':0,'failure_count':0,'byte_count':0,'error_code':None,'error_summary':None}
    row=dict(oldrow,id=101,run_id='d2e3a86f-27a4-4c2a-be21-b512eebf1216',attempt=2,started_at='2026-10-10T23:31:00Z',ended_at='2026-10-10T23:31:00Z',status='SKIPPED',error_code='ALREADY_SUCCESSFUL',error_summary='step already successful for business date')
    old={'schubert.batch_runs':[oldrow],'schubert.inbox_inspection_progress':[{'fixed':'old'}]};new=copy.deepcopy(old);new['schubert.batch_runs'].append(row)
    cut=datetime.datetime(2026,10,10,23,30,tzinfo=datetime.timezone.utc);end=cut+datetime.timedelta(minutes=5)
    native={'/run/schubert-nk/pt-coverage/ordinary-inspector196/old.exec':{'sha256':'a'*64}}
    return old,new,row['run_id'],cut,end,native,copy.deepcopy(native)

class DailySkipOracleTest(unittest.TestCase):
    def test_independent_skip_not_fresh_inspector_success(self):
        result=qualify(*fixture());self.assertTrue(result['dailyInspectorSkipVerified']);self.assertFalse(result['newInspectorNativeAccepted'])

    def test_boundary_null_counts_reason_duplicated_changed_progress_and_native(self):
        for key,bad in [('id',100),('attempt',1),('status','SUCCESS'),('business_date','2026-10-10'),('error_code',None),('error_summary','raw'),('ended_at','2026-10-10T23:32:00Z'),('started_at','2026-10-10T23:29:00Z'),('target_count',1),('success_count',True),('failure_count',None),('byte_count',-1)]:
            args=list(fixture());args[1]['schubert.batch_runs'][-1][key]=bad
            with self.assertRaises(ValueError):qualify(*args)
        for index,bad in [(0,None),(1,None),(2,None),(3,None),(4,None),(5,None),(6,None)]:
            args=list(fixture());args[index]=bad
            with self.assertRaises(ValueError):qualify(*args)
        for change in ['duplicateSuccess','progress','native','changedOld']:
            args=list(fixture())
            if change=='duplicateSuccess':args[0]['schubert.batch_runs'].append(dict(args[0]['schubert.batch_runs'][0],id=99));args[1]['schubert.batch_runs'].insert(0,args[0]['schubert.batch_runs'][-1])
            elif change=='progress':args[1]['schubert.inbox_inspection_progress'].append({'run':'unexpected'})
            elif change=='native':args[6]['/run/schubert-nk/pt-coverage/ordinary-inspector196/new.exec']={'sha256':'b'*64}
            else:args[1]['schubert.batch_runs'][0]['status']='FAILED'
            with self.assertRaises(ValueError):qualify(*args)

if __name__=='__main__':unittest.main()
