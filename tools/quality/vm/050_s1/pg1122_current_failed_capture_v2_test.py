"""Independent fresh/mixed ten-step vector; no old all-SKIP success borrowing."""
import ast
import copy
import unittest
import pg1120_current_failed_capture_test as original_fixture
from pg1122_current_failed_capture_v2 import payload


class CorrectedCaptureTest(unittest.TestCase):
    def test_corrected_eight_skip_and_two_backup_classification(self):
        fixture=original_fixture.FailedCaptureTest();before,values=fixture.fixture()
        for row in values['schubert.batch_runs'][594:]:
            if row['step']=='BACKUP_DB':
                row.update(status='SUCCESS',error_code=None,error_summary=None,
                           target_count=1,success_count=1,byte_count=13)
            elif row['step']=='BACKUP_CONFIG':
                row.update(status='SUCCESS',error_code=None,error_summary=None,
                           target_count=2,success_count=2,byte_count=35)
        tree=ast.parse(payload())
        nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in {'require','row_oracle'}]
        env={'RUN':'343a5a1b-d064-47d5-88c2-31c36d7ba7a4','baseline':{'rows':before}}
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'<independent mixed fresh fixture>','exec'),env)
        env['row_oracle'](values)
        value=copy.deepcopy(values);value['schubert.batch_runs'][-1]['status']='SUCCESS'
        with self.assertRaises(ValueError):env['row_oracle'](value)
        old=fixture.namespace();old['baseline']={'rows':before}
        with self.assertRaises(ValueError):old['row_oracle'](values)

    def test_fresh_input_binding_new_slot_and_no_mutations(self):
        text=payload();ast.parse(text)
        for required in ['failed-capture-v2',"kind=='backup':pass",'backup.qualify(RUN,CUTOFF,',
                         "baseline['artifacts']['config/effective/backup-profile.json']",
                         "'cleanupEightExactSkip':True","'freshBackupTwoSuccessVerified':True"]:
            self.assertTrue(required in text)
        self.assertFalse('failed-capture-v1' in text or 'new10ExactSkip' in text)
        self.assertFalse('systemctl start' in text or 'systemctl stop' in text)


if __name__=='__main__':unittest.main()
