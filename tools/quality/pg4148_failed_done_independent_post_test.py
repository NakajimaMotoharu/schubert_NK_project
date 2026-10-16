import ast
import unittest
from pyflakes.api import check
import pg4148_failed_done_independent_post as subject
from pg4058_original_read_profile_test import guards
import pg4058_original_read_profile_test as original_fixtures


class IndependentPostTest(unittest.TestCase):
    def test_complete_closure_is_readonly_and_binds_prior_fixed_cohort(self):
        raw=subject.payload()
        self.assertEqual(0,check(raw,'<independent failed-DONE post>'))
        self.assertFalse(hasattr(subject,'main'))
        for expected in ['fd1177d10f2713596a32de536a3c71d592563cc3b6decb7194bc6c68ea6c21d8',
                         'before[\'database\'][\'rows\']','terminal_contract.kernel_empty(unit)',
                         "epoch_contract['former_issued']", "native_contract['preserved']", "signed_contract['verify']",
                         'RootOriginalReadProfile', 'receipt[\'oldParentNormal\']is False',
                         'independentFailedDoneRecoveryPost','nativeQualificationPending']:
            self.assertTrue(expected in raw)
        for forbidden in ["'/usr/bin/systemctl','stop'",'RECOVERY_STOP','RECOVERY_REVOKED','reset-failed','os.kill(']:
            self.assertFalse(forbidden in raw)

    def test_actual_zero_pool_or_one_owned_socket_never_old_ordinary_three(self):
        raw=subject.payload();value,unused,sockets=original_fixtures.GuardTest().fixture(True)
        value['database']['peers']=[row for row in value['database']['peers']if row['pid']==240]
        row=value['database']['peers'][0];port=row['port']
        table='header\n'+f'0: 0100007F:{port:04X} 0100007F:1538 01 0 0 0 0 0 900\n'+f'0: 0100007F:1538 0100007F:{port:04X} 01 0 0 0 0 0 901'
        ns=guards({'/proc/net/tcp':table,'/proc/net/tcp6':'header'},{140:{'900'},240:{'901'}},raw)
        ns['peers'](value,(140,240))
        value['database']['peers'].append(dict(row))
        with self.assertRaises(ValueError):ns['peers'](value,(140,240))
        value['database']['peers']=[];value['database']['locks']=[];value['flocks']=[]
        ns['peers'](value)
        value['database']['peers']=[row]
        with self.assertRaises(ValueError):ns['peers'](value)

    def test_all_snapshot_paths_use_independent_signed_native_terminal_epoch_oracles(self):
        raw=subject.payload();tree=ast.parse(raw)
        wrapper=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='snapshot'][-1]
        called=ast.unparse(wrapper)
        for key in ['signed_contract','native_contract','epoch_contract','parent_contract','terminal_contract']:
            self.assertTrue(key in called)
        for key in ['durable','runtime','database','startup','actors']:
            self.assertTrue(repr(key) in called)
        self.assertTrue('reference' in called)


if __name__=='__main__':unittest.main()
