"""Actual embedded independent manifest fixture and continuous fresh Ref lifetime."""
import ast
import copy
import hashlib
import json
import unittest
from pg1619_current_ordinary_backup_qualification import payload

class CurrentBackupQualificationTest(unittest.TestCase):
    def test_actual_embedded_manifest_literal_bytes_and_all_handle_fields(self):
        raw=payload();tree=ast.parse(raw)
        function=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='qualify_backup')
        source=next(ast.literal_eval(n.value)for n in function.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ORACLE_SOURCE'for t in n.targets))
        env={};exec(compile(source,'<actual independent embedded Backup contract>','exec'),env)
        run='0be226b1-bbb7-43d3-aa9e-59d0bda70f9a';cut='2026-10-12T06:23:13.176261Z';start='2026-10-12T06:23:18.000000Z';finish='2026-10-12T06:23:20.000000Z'
        profile={'host':'pgpt-r2','app':'0.1.0-SNAPSHOT','schema':'028','os':'ubuntu-26.04','jdk':'25.0.4','postgresql':'18.6','artemis':'2.56.0','age':'1.2.1'}
        files={n:{'size':size,'sha256':'a'*64}for n,size in [('schubert_nk.dump',11),('config.tar',13),('credentials.tar.age',17)]}
        recipient=hashlib.sha256(b'fixture public recipient').hexdigest()
        m={'format':'NKBACKUP1','database':'schubert_nk','runId':run,'cutoff':cut,'startedAt':start,'contentFinishedAt':finish,'databaseStep':{'id':1001,'attempt':3,'startedAt':start},'configurationStep':{'id':1002,'attempt':3,'startedAt':start},'versions':profile,'recipientSha256':recipient,'files':files}
        rows=[{'id':i,'attempt':3,'run_id':run,'business_date':'2026-10-12','step':step,'started_at':start,'ended_at':'2026-10-12T06:23:21.000000Z','status':'SUCCESS','target_count':count,'success_count':count,'failure_count':0,'byte_count':size,'error_code':None,'error_summary':None}for i,step,count,size in [(1001,'BACKUP_DB',1,11),(1002,'BACKUP_CONFIG',2,30)]]
        encode=lambda v:(json.dumps(v,separators=(',',':'))+'\n').encode()
        result=env['verify'](encode(m),files,profile,rows,run,cut,recipient)
        self.assertEqual(result['directoryName'],'20261012-152318-'+run);self.assertEqual(result['totalArchiveBytes'],41)
        for key,bad in [('status','SKIPPED'),('byte_count',0),('attempt',2),('error_code','ALREADY_SUCCESSFUL'),('business_date','2026-10-11'),('id',True)]:
            changed=copy.deepcopy(rows);changed[0][key]=bad
            with self.assertRaises(ValueError):env['verify'](encode(m),files,profile,changed,run,cut,recipient)
        self.assertIn("retiredOlderGenerationPrivateBytesQualificationPending':True",raw)

    def test_whole_scope_and_real_reader_are_not_after_unref(self):
        raw=payload();tree=ast.parse(raw)
        life=next(n for n in tree.body if isinstance(n,ast.Try)and any(isinstance(v,ast.Call)and isinstance(v.func,ast.Attribute)and v.func.attr=='RefUnit'for v in ast.walk(n)))
        body=ast.unparse(ast.Module(body=life.body,type_ignores=[]));final=ast.unparse(ast.Module(body=life.finalbody,type_ignores=[]))
        self.assertIn('backup_result, listing_bytes = qualify_backup()',body);self.assertIn('native == snapshot()',body)
        self.assertIn('UnrefUnit',final);self.assertIn('bus.close()',final)
        self.assertIn('pg1609-native-stop-v1',raw);self.assertIn('d28eead2-941c-4b97-9747-1758c0809e29.done',raw)
        self.assertIn('ordinaryPgRestoreListExit',raw);self.assertNotIn('StartUnit',raw);self.assertNotIn('StopUnit',raw)

if __name__=='__main__':unittest.main()
