"""Independent SQL fixture adapted as input, not Production-generated expected."""
import ast
import copy
import unittest
from pg1602_current_newrun_rows_oracle_test import NewRunSqlOracleTest
from pg1702_new_source_completed_seal import payload


class NewSourceSealTest(unittest.TestCase):
    def test_sql_oracle_new_run_and_failure_boundaries(self):
        raw=payload();tree=ast.parse(raw)
        oracle=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)
                    and any(isinstance(t,ast.Name)and t.id=='ORACLE'for t in n.targets))
        env={};exec(compile(oracle,'<independent SQL fixture>','exec'),env)
        old,new=NewRunSqlOracleTest().fixture()
        # Fixed input translation only; asserted results are independent SS literals.
        def translate(v):
            if isinstance(v,dict):return{k:translate(x)for k,x in v.items()}
            if isinstance(v,list):return[translate(x)for x in v]
            if isinstance(v,str):return v.replace('0be226b1-bbb7-43d3-aa9e-59d0bda70f9a','02e941b9-1c52-4018-a193-63dd00b269af').replace('T06:','T14:')
            return v
        old,new=translate(old),translate(new)
        for row in new['schubert.batch_runs'][10:12]:
            count=1 if row['step']=='BACKUP_DB'else 2
            row.update(status='SUCCESS',error_code=None,error_summary=None,target_count=count,success_count=count,byte_count=100)
        args=('2026-10-12T14:19:28.968927Z','2026-10-12T14:30:00Z','2026-10-12T14:45:00Z')
        result=env['qualify'](old,new,*args)
        self.assertEqual(2,result['freshBackupSuccessSteps']);self.assertEqual(8,result['newSkippedSteps'])
        self.assertEqual(1,result['newSentOutbox']);self.assertTrue(result['backupBundleByteOraclePending'])
        for table,index,key,bad in [('schubert.batch_runs',10,'run_id','0be226b1-bbb7-43d3-aa9e-59d0bda70f9a'),
                                    ('schubert.batch_runs',10,'status','SKIPPED'),
                                    ('schubert.batch_runs',11,'byte_count',0),
                                    ('schubert.batch_runs',10,'ended_at','2026-10-12T14:31:00Z'),
                                    ('schubert_web_session.web_log_outbox',0,'sent_at','2026-10-12T14:46:00Z')]:
            changed=copy.deepcopy(new);changed[table][index][key]=bad
            with self.subTest(table=table,key=key),self.assertRaises(ValueError):env['qualify'](old,changed,*args)
        self.assertIn('pg1699-new-current-ordinary-once-v1/before.private.json',raw)
        self.assertIn('ef9ddffcf813c6e4f4b8bb6379c30e5e0d87503a4abaf46859976a32fa8bfecb',raw)
        self.assertIn('old[\'unitFilesActual\']=before[\'unitFilesActual\']',raw)
        self.assertNotIn('StartUnit',raw);self.assertNotIn('StopUnit',raw)
        life=next(n for n in tree.body if isinstance(n,ast.Try))
        self.assertIn('UnrefUnit',ast.unparse(ast.Module(body=life.finalbody,type_ignores=[])))


if __name__=='__main__':unittest.main()
