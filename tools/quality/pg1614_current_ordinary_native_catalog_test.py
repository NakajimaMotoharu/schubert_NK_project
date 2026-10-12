"""Independent actual Backup PID1 windows/old generations, no guest operations."""
import ast
import copy
import unittest
from pg1614_current_ordinary_native_catalog import catalog_source
from pg1615_current_ordinary_native_qualification import source

class OrdinaryNativeTest(unittest.TestCase):
    def test_actual_backup_pid1_contract_and_foreign_fields(self):
        raw=catalog_source();tree=ast.parse(raw)
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='backup_window')
        env={};exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual ordinary Backup PID1 oracle>','exec'),env)
        common={'_BOOT_ID':'3d69f5af6bac46b1a5407591c4a79a0d','_PID':'1','_UID':'0','_COMM':'systemd','UNIT':'schubert-nk-backup.service','INVOCATION_ID':'1c085a5e6e874ba1b0d647c92ab3c34c','__REALTIME_TIMESTAMP':'1791786200000000'}
        rows=[dict(common,__CURSOR='fixture'+str(i),__MONOTONIC_TIMESTAMP=str(stamp),MESSAGE_ID=mid,**extra)for i,(stamp,mid,extra)in enumerate([(38378028532,'7d4958e842da4a758f6c1cdc7b36dcc5',{'JOB_ID':'71347','JOB_TYPE':'start'}),(38380559450,'39f53479d3a045ac8e11786248231fbf',{'JOB_ID':'71347','JOB_TYPE':'start','JOB_RESULT':'done'}),(38381232981,'7ad2d189f7e94e70a38c781354912448',{}),(38381233265,'9d1aaa27d60140bd96365438aad20286',{'JOB_ID':'71494','JOB_TYPE':'stop','JOB_RESULT':'done'})])]
        self.assertEqual(env['backup_window'](rows),(38378028532,38381232981))
        for index in range(4):
            for key in ['_BOOT_ID','_PID','_UID','_COMM','UNIT','INVOCATION_ID','__MONOTONIC_TIMESTAMP','__REALTIME_TIMESTAMP','__CURSOR','MESSAGE_ID']:
                changed=copy.deepcopy(rows);changed[index][key]='fixture'+str((index+1)%4)if key=='__CURSOR'else'foreign'
                with self.assertRaises(ValueError):env['backup_window'](changed)
        for bad in [None,[],rows+[rows[0]]]:
            with self.assertRaises(ValueError):env['backup_window'](bad)
        self.assertIn('len(old)==10',raw);self.assertIn('oldTenArchiveUnchanged',raw)
        self.assertIn('pg1600-current-ordinary-once-v2',raw);self.assertIn('pg1609-native-stop-v1',raw)
        self.assertIn("'JOB_ID')=='71184'",raw);self.assertIn('39951854181',raw)
        transport=source();self.assertIn('pg1614-current-ordinary-native-catalog-v1',transport);self.assertIn('PG1615',transport)
        self.assertIn("check(source,'<actual current server native payload>'",transport)

if __name__=='__main__':unittest.main()
