"""Independent mixed Backup/skip literals; old resume expectation must fail."""
import copy
import ast
import unittest
from pg1602_current_newrun_rows_oracle_test import NewRunSqlOracleTest
from pg1605_current_ordinary_rows_oracle_v2 import qualify
from pg1606_current_ordinary_full_seal_v2 import payload

class OrdinarySqlTest(unittest.TestCase):
    def test_new_backup_and_eight_skips_foreign_and_failure_vectors(self):
        old,new=NewRunSqlOracleTest().fixture()
        for r in new['schubert.batch_runs'][10:12]:
            count=1 if r['step']=='BACKUP_DB'else 2
            r.update(status='SUCCESS',error_code=None,error_summary=None,target_count=count,success_count=count,byte_count=100)
        lower='2026-10-12T06:23:13.176261Z';upper='2026-10-12T06:45:00Z'
        value=qualify(old,new,lower,upper)
        self.assertEqual(value['freshBackupSuccessSteps'],2);self.assertEqual(value['newSkippedSteps'],8);self.assertTrue(value['backupBundleByteOraclePending'])
        for index,key,bad in [(10,'status','SKIPPED'),(11,'byte_count',0),(11,'target_count',1),(12,'status','SUCCESS'),(10,'attempt',1),(10,'error_code','ALREADY_SUCCESSFUL'),(10,'run_id','15700a87-9117-4f63-a0ff-768dd604d0f1'),(10,'business_date','2026-10-11'),(10,'ended_at','2026-10-13T00:00:00Z')]:
            changed=copy.deepcopy(new);changed['schubert.batch_runs'][index][key]=bad
            with self.assertRaises(ValueError):qualify(old,changed,lower,upper)
        raw=payload();ast.parse(raw)
        self.assertIn("before['oneTimeRuntime']=before['runtime']",raw)
        self.assertIn("**before['extraDurable']",raw)
        self.assertIn("'backupManifestRetentionOraclePending':True",raw)
        self.assertIn('pg1606-current-ordinary-full-seal-v2',raw)
        self.assertNotIn("proof.result['endInstant']",raw)

if __name__=='__main__':unittest.main()
