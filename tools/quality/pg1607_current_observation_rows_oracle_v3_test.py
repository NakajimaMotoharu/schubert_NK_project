"""Hand-written post-DONE Web, pre-DONE batch and strict independent limits."""
import copy
import unittest
from pg1602_current_newrun_rows_oracle_test import NewRunSqlOracleTest
from pg1607_current_observation_rows_oracle_v3 import qualify
from pg1608_current_observation_full_seal_v3 import payload

class ObservationBoundTest(unittest.TestCase):
    def test_post_done_http_is_not_post_done_batch(self):
        old,new=NewRunSqlOracleTest().fixture()
        for r in new['schubert.batch_runs'][10:12]:
            count=1 if r['step']=='BACKUP_DB'else 2
            r.update(status='SUCCESS',error_code=None,error_summary=None,target_count=count,success_count=count,byte_count=100)
        args=('2026-10-12T06:23:13.176261Z','2026-10-12T06:30:00Z','2026-10-12T06:45:00Z')
        self.assertEqual(qualify(old,new,*args)['newSentOutbox'],1)
        for table,index,key,bad in [('schubert.batch_runs',10,'ended_at','2026-10-12T06:31:00Z'),('schubert_web_session.web_log_outbox',0,'sent_at','2026-10-12T06:46:00Z')]:
            changed=copy.deepcopy(new);changed[table][index][key]=bad
            with self.assertRaises(ValueError):qualify(old,changed,*args)
        for done,observed in [(None,args[2]),(args[1],None),('2026-10-12T06:50:00Z',args[2])]:
            with self.assertRaises((ValueError,TypeError)):qualify(old,new,args[0],done,observed)
        raw=payload();self.assertEqual(raw.count('OBSERVED_UPPER=datetime.datetime.now'),1)
        self.assertIn("proof.done.decode('ascii').splitlines()[4],OBSERVED_UPPER)",raw)
        self.assertIn("'backupManifestRetentionOraclePending':True",raw)

if __name__=='__main__':unittest.main()
